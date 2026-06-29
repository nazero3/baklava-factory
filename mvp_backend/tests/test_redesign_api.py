"""Tests for the redesign: list endpoints, reject flows, reorder_level low-stock,
enriched inventory, enriched dashboard summary, and reports."""


def _bootstrap(client, headers):
    supplier = client.post("/suppliers", json={"name": "Golden Nuts"}, headers=headers).json()
    store = client.post("/stores", json={"name": "Downtown Store"}, headers=headers).json()
    flour = client.post(
        "/products",
        json={"code": "RM-FLOUR", "name": "Flour", "category": "raw", "reorder_level": 100},
        headers=headers,
    ).json()
    nuts = client.post(
        "/products",
        json={"code": "RM-NUTS", "name": "Pistachio", "category": "raw"},
        headers=headers,
    ).json()
    baklava = client.post(
        "/products",
        json={"code": "FG-BAKLAVA", "name": "Baklava", "category": "finished"},
        headers=headers,
    ).json()
    client.post(
        "/recipes",
        json={
            "finished_product_id": baklava["id"],
            "items": [
                {"ingredient_product_id": flour["id"], "qty_per_kg_output": 0.6},
                {"ingredient_product_id": nuts["id"], "qty_per_kg_output": 0.4},
            ],
        },
        headers=headers,
    )
    for pid, qty, cost in [(flour["id"], 50, 1.2), (nuts["id"], 30, 5.0)]:
        client.post(
            "/receivings",
            json={"supplier_id": supplier["id"], "product_id": pid, "qty_kg": qty, "unit_cost": cost, "lot_no": "LOT-1"},
            headers=headers,
        )
    client.post(
        "/production/batches/complete",
        json={"finished_product_id": baklava["id"], "target_kg": 10, "actual_kg": 10, "waste_kg": 0.2},
        headers=headers,
    )
    dispatch = client.post(
        "/transfers/dispatch",
        json={"product_id": baklava["id"], "qty_kg": 6, "to_store_id": store["id"]},
        headers=headers,
    ).json()
    return {"supplier": supplier, "store": store, "flour": flour, "nuts": nuts, "baklava": baklava, "transfer": dispatch}


def test_product_create_accepts_reorder_level(client, admin_headers):
    resp = client.post(
        "/products",
        json={"code": "RM-X", "name": "Sugar", "category": "raw", "reorder_level": 25},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    products = client.get("/products?category=raw", headers=admin_headers).json()
    sugar = next(p for p in products if p["code"] == "RM-X")
    assert sugar["reorder_level"] == 25


def test_list_endpoints_return_named_rows(client, admin_headers):
    data = _bootstrap(client, admin_headers)

    stores = client.get("/stores/list", headers=admin_headers).json()
    assert any(s["id"] == data["store"]["id"] for s in stores)

    recipes = client.get("/recipes", headers=admin_headers).json()
    assert recipes and recipes[0]["finished_name"] == "Baklava"
    assert len(recipes[0]["items"]) == 2
    assert recipes[0]["items"][0]["ingredient_name"]

    receivings = client.get("/receivings", headers=admin_headers).json()
    assert len(receivings) == 2
    assert receivings[0]["supplier_name"] == "Golden Nuts"
    assert receivings[0]["product_name"]

    batches = client.get("/production/batches", headers=admin_headers).json()
    assert len(batches) == 1 and batches[0]["finished_name"] == "Baklava"

    transfers = client.get("/transfers", headers=admin_headers).json()
    assert len(transfers) == 1
    assert transfers[0]["to_store_name"] == "Downtown Store"
    assert transfers[0]["product_name"] == "Baklava"

    users = client.get("/auth/users", headers=admin_headers).json()
    assert any(u["username"] == "admin" for u in users)


def test_inventory_is_enriched_with_value_and_names(client, admin_headers):
    _bootstrap(client, admin_headers)
    rows = client.get("/inventory", headers=admin_headers).json()
    assert rows
    flour_row = next(r for r in rows if r["product_code"] == "RM-FLOUR")
    assert flour_row["product_name"] == "Flour"
    assert flour_row["location_name"] == "Factory"
    assert flour_row["value"] == round(flour_row["quantity_kg"] * flour_row["weighted_cost_per_kg"], 2)


def test_store_movements_list(client, admin_headers):
    data = _bootstrap(client, admin_headers)
    store_id = data["store"]["id"]
    transfer_id = data["transfer"]["id"]
    client.post(f"/transfers/{transfer_id}/receive", json={"received_qty_kg": 6}, headers=admin_headers)
    client.post(
        f"/stores/{store_id}/movements",
        json={"product_id": data["baklava"]["id"], "movement_type": "sale", "qty_kg": 2},
        headers=admin_headers,
    )
    movements = client.get("/store-movements", headers=admin_headers).json()
    assert movements and movements[0]["store_name"] == "Downtown Store"
    assert movements[0]["movement_type"] == "sale"


def test_transfer_exception_reject_flow(client, admin_headers):
    data = _bootstrap(client, admin_headers)
    transfer_id = data["transfer"]["id"]
    # Received less than dispatched by more than the auto-approve threshold -> pending exception.
    client.post(f"/transfers/{transfer_id}/receive", json={"received_qty_kg": 5.5}, headers=admin_headers)

    exceptions = client.get("/transfer-exceptions", headers=admin_headers).json()
    assert len(exceptions) == 1
    exc = exceptions[0]
    assert exc["status"] == "pending"

    reject = client.post(f"/transfer-exceptions/{exc['id']}/reject", headers=admin_headers)
    assert reject.status_code == 200
    assert reject.json()["status"] == "rejected"

    # Rejecting again should fail because it is no longer pending.
    again = client.post(f"/transfer-exceptions/{exc['id']}/reject", headers=admin_headers)
    assert again.status_code == 400


def test_inventory_adjustment_list_and_reject(client, admin_headers):
    data = _bootstrap(client, admin_headers)
    # delta magnitude > 1 kg stays pending.
    created = client.post(
        "/inventory/adjustments",
        json={
            "location_type": "factory",
            "location_id": 0,
            "product_id": data["flour"]["id"],
            "qty_delta_kg": -3.0,
            "reason": "Spillage",
        },
        headers=admin_headers,
    ).json()
    assert created["status"] == "pending"

    adjustments = client.get("/inventory/adjustments", headers=admin_headers).json()
    assert any(a["id"] == created["adjustment_id"] and a["product_name"] == "Flour" for a in adjustments)

    reject = client.post(f"/inventory/adjustments/{created['adjustment_id']}/reject", headers=admin_headers)
    assert reject.status_code == 200
    assert reject.json()["status"] == "rejected"


def test_dashboard_summary_is_enriched(client, admin_headers):
    _bootstrap(client, admin_headers)
    summary = client.get("/dashboard/daily-summary", headers=admin_headers).json()
    assert "inventory_value" in summary and summary["inventory_value"] > 0
    assert "pending_approvals" in summary and "total" in summary["pending_approvals"]
    assert isinstance(summary["recent_activity"], list) and summary["recent_activity"]
    # Flour received 50 kg with reorder level 100 -> low stock.
    assert summary["low_stock_count"] >= 1
    assert any(item["code"] == "RM-FLOUR" for item in summary["low_stock"])


def test_reports(client, admin_headers):
    _bootstrap(client, admin_headers)

    inv_value = client.get("/reports/inventory-value", headers=admin_headers).json()
    assert inv_value["report"] == "inventory-value"
    assert any(row["category"] == "raw" for row in inv_value["rows"])

    low_stock = client.get("/reports/low-stock", headers=admin_headers).json()
    assert any(row["code"] == "RM-FLOUR" for row in low_stock["rows"])

    yield_report = client.get("/reports/production-yield", headers=admin_headers).json()
    assert yield_report["rows"] and yield_report["rows"][0]["yield_pct"] == 100.0

    unknown = client.get("/reports/does-not-exist", headers=admin_headers)
    assert unknown.status_code == 404


def test_dashboard_summary_visible_to_non_privileged_role(client, admin_headers):
    # store_manager is not in the old summary allow-list; should now be allowed.
    client.post(
        "/auth/users",
        json={"username": "sm1", "full_name": "Store Manager", "password": "pass1234", "role": "store_manager"},
        headers=admin_headers,
    )
    login = client.post("/auth/login", json={"username": "sm1", "password": "pass1234"})
    token = login.json()["access_token"]
    resp = client.get("/dashboard/daily-summary", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
