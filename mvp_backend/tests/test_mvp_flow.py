from sqlalchemy.orm import Session

from app.auth import hash_password
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import User, UserRole


client = TestClient(app)


def test_end_to_end_mvp_flow():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    db.add(
        User(
            username="admin",
            full_name="System Administrator",
            password_hash=hash_password("admin123"),
            role=UserRole.admin,
            is_active=True,
        )
    )
    db.commit()
    db.close()

    login = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    user_resp = client.post(
        "/auth/users",
        json={
            "username": "store1_manager",
            "full_name": "Store 1 Manager",
            "password": "store123",
            "role": "store_manager",
        },
        headers=headers,
    )
    assert user_resp.status_code == 200

    supplier = client.post("/suppliers", json={"name": "Golden Nuts Supplier"}, headers=headers).json()
    store = client.post("/stores", json={"name": "Store 1"}, headers=headers).json()

    flour = client.post("/products", json={"code": "RM-FLOUR", "name": "Flour", "category": "raw"}, headers=headers).json()
    nuts = client.post("/products", json={"code": "RM-NUTS", "name": "Pistachio", "category": "raw"}, headers=headers).json()
    baklava = client.post(
        "/products",
        json={"code": "FG-BAKLAVA", "name": "Baklava Classic", "category": "finished"},
        headers=headers,
    ).json()
    duplicate_product = client.post(
        "/products",
        json={"code": "FG-BAKLAVA", "name": "Baklava Duplicate", "category": "finished"},
        headers=headers,
    )
    assert duplicate_product.status_code == 409

    recipe_payload = {
        "finished_product_id": baklava["id"],
        "items": [
            {"ingredient_product_id": flour["id"], "qty_per_kg_output": 0.6},
            {"ingredient_product_id": nuts["id"], "qty_per_kg_output": 0.4},
        ],
    }
    recipe_resp = client.post("/recipes", json=recipe_payload, headers=headers)
    assert recipe_resp.status_code == 200

    for product_id, qty, cost in [(flour["id"], 50, 1.2), (nuts["id"], 30, 5.0)]:
        recv_resp = client.post(
            "/receivings",
            json={"supplier_id": supplier["id"], "product_id": product_id, "qty_kg": qty, "unit_cost": cost, "lot_no": "LOT-1"},
            headers=headers,
        )
        assert recv_resp.status_code == 200

    prod_resp = client.post(
        "/production/batches/complete",
        json={"finished_product_id": baklava["id"], "target_kg": 10, "actual_kg": 10, "waste_kg": 0.2},
        headers=headers,
    )
    assert prod_resp.status_code == 200

    dispatch_resp = client.post(
        "/transfers/dispatch",
        json={"product_id": baklava["id"], "qty_kg": 6, "to_store_id": store["id"]},
        headers=headers,
    )
    assert dispatch_resp.status_code == 200
    transfer_id = dispatch_resp.json()["id"]

    receive_resp = client.post(f"/transfers/{transfer_id}/receive", json={"received_qty_kg": 5.5}, headers=headers)
    assert receive_resp.status_code == 200

    sale_resp = client.post(
        f"/stores/{store['id']}/movements",
        json={"product_id": baklava["id"], "movement_type": "sale", "qty_kg": 2},
        headers=headers,
    )
    assert sale_resp.status_code == 200

    waste_resp = client.post(
        f"/stores/{store['id']}/movements",
        json={"product_id": baklava["id"], "movement_type": "waste", "qty_kg": 0.3},
        headers=headers,
    )
    assert waste_resp.status_code == 200

    adjustment_resp = client.post(
        "/inventory/adjustments",
        json={
            "location_type": "factory",
            "location_id": 0,
            "product_id": flour["id"],
            "qty_delta_kg": -2.0,
            "reason": "Damaged bag",
        },
        headers=headers,
    )
    assert adjustment_resp.status_code == 200
    adjustment_id = adjustment_resp.json()["adjustment_id"]
    approve_resp = client.post(f"/inventory/adjustments/{adjustment_id}/approve", headers=headers)
    assert approve_resp.status_code == 200

    csv_payload = "code,name,category,unit\nFG-BAKLAVA2,Baklava Premium,finished,kg\n"
    import_resp = client.post(
        "/import/products-csv",
        files={"file": ("products.csv", csv_payload, "text/csv")},
        headers=headers,
    )
    assert import_resp.status_code == 200
    assert import_resp.json()["imported_rows"] == 1

    export_products = client.get("/export/products-csv", headers=headers)
    assert export_products.status_code == 200
    assert "FG-BAKLAVA2" in export_products.text

    dashboard = client.get("/dashboard/daily-summary", headers=headers)
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["produced_kg"] >= 10
    assert body["sales_kg"] >= 2
