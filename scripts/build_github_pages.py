#!/usr/bin/env python3
"""Build a static GitHub Pages preview of the ERP web UI."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = REPO_ROOT / "mvp_backend" / "app" / "static"
OUT_DIR = REPO_ROOT / "github-pages"

# Project Pages URL: https://<user>.github.io/<repo-name>/
_REPO_NAME = os.environ.get("GITHUB_REPOSITORY", "nazero3/baklava-factory").rsplit("/", 1)[-1]
BASE_PATH = f"/{_REPO_NAME}"

ROUTE_TO_FILE = {
    "/": "dashboard.html",
    "/login": "login.html",
    "/dashboard": "dashboard.html",
    "/suppliers": "supplier.html",
    "/stores": "stores.html",
    "/products-view": "products.html",
    "/recipes-view": "recipes.html",
    "/receiving": "receiving.html",
    "/production": "production.html",
    "/dispatch": "dispatch.html",
    "/store-return": "store-return.html",
    "/inventory-view": "inventory.html",
    "/approvals": "approvals.html",
    "/reports": "reports.html",
    "/users": "users.html",
}

# Sample data shown on GitHub Pages (no backend available there).
DEMO_GET_RESPONSES: dict[str, object] = {
    "/dashboard/daily-summary": {
        "raw_stock_kg": 68.0,
        "finished_stock_kg": 7.2,
        "produced_kg": 45.5,
        "waste_kg": 1.2,
        "sales_kg": 12.8,
        "inventory_value": 199.98,
        "low_stock_count": 1,
        "low_stock": [
            {
                "product_id": 1,
                "code": "RM-FLOUR",
                "name": "Flour",
                "quantity_kg": 8.5,
                "reorder_level": 10.0,
            }
        ],
        "pending_approvals": {"adjustments": 1, "transfer_exceptions": 0, "total": 1},
        "recent_activity": [
            {
                "type": "receiving",
                "created_at": "2026-06-28T09:15:00",
                "product": "Pistachio",
                "qty_kg": 50.0,
                "detail": "lot L-1001",
            },
            {
                "type": "production",
                "created_at": "2026-06-28T11:30:00",
                "product": "Baklava Assorted",
                "qty_kg": 12.0,
                "detail": "waste 0.3 kg",
            },
            {
                "type": "transfer",
                "created_at": "2026-06-28T14:00:00",
                "product": "Baklava Assorted",
                "qty_kg": 6.0,
                "detail": "dispatched",
            },
            {
                "type": "sale",
                "created_at": "2026-06-28T16:45:00",
                "product": "Baklava Assorted",
                "qty_kg": 2.5,
                "detail": "",
            },
        ],
    },
    "/suppliers/list": [
        {"id": 1, "name": "Syrian Pistachio Co."},
        {"id": 2, "name": "Damascus Sugar Mills"},
    ],
    "/stores/list": [
        {"id": 1, "name": "Store Damascus"},
        {"id": 2, "name": "Store Aleppo"},
        {"id": 3, "name": "Store Homs"},
    ],
    "/products": [
        {
            "id": 1,
            "code": "RM-FLOUR",
            "name": "Flour",
            "category": "raw",
            "unit": "kg",
            "reorder_level": 10.0,
        },
        {
            "id": 2,
            "code": "RM-PIST",
            "name": "Pistachio",
            "category": "raw",
            "unit": "kg",
            "reorder_level": 5.0,
        },
        {
            "id": 3,
            "code": "FG-BAKL",
            "name": "Baklava Assorted",
            "category": "finished",
            "unit": "kg",
            "reorder_level": 0.0,
        },
    ],
    "/receivings": [
        {
            "id": 1,
            "supplier_id": 1,
            "supplier_name": "Syrian Pistachio Co.",
            "product_id": 2,
            "product_name": "Pistachio",
            "qty_kg": 50.0,
            "unit_cost": 18.5,
            "lot_no": "L-1001",
            "created_at": "2026-06-28T09:15:00",
        }
    ],
    "/production/batches": [
        {
            "id": 1,
            "finished_product_id": 3,
            "finished_name": "Baklava Assorted",
            "target_kg": 12.0,
            "actual_kg": 11.7,
            "waste_kg": 0.3,
            "created_at": "2026-06-28T11:30:00",
        }
    ],
    "/transfers": [
        {
            "id": 1,
            "product_id": 3,
            "product_name": "Baklava Assorted",
            "qty_kg": 6.0,
            "to_store_id": 1,
            "to_store_name": "Store Damascus",
            "status": "received",
            "created_at": "2026-06-28T14:00:00",
        }
    ],
    "/store-movements": [
        {
            "id": 1,
            "store_id": 1,
            "store_name": "Store Damascus",
            "product_id": 3,
            "product_name": "Baklava Assorted",
            "movement_type": "sale",
            "qty_kg": 2.5,
            "unit_price": 45.0,
            "created_at": "2026-06-28T16:45:00",
        }
    ],
    "/inventory": [
        {
            "location_type": "factory",
            "location_id": 0,
            "location_name": "Factory",
            "product_id": 1,
            "product_code": "RM-FLOUR",
            "product_name": "Flour",
            "quantity_kg": 8.5,
            "weighted_cost_per_kg": 1.2,
            "value": 10.2,
        },
        {
            "location_type": "factory",
            "location_id": 0,
            "location_name": "Factory",
            "product_id": 3,
            "product_code": "FG-BAKL",
            "product_name": "Baklava Assorted",
            "quantity_kg": 7.2,
            "weighted_cost_per_kg": 26.35,
            "value": 189.72,
        },
        {
            "location_type": "store",
            "location_id": 1,
            "location_name": "Store Damascus",
            "product_id": 3,
            "product_code": "FG-BAKL",
            "product_name": "Baklava Assorted",
            "quantity_kg": 3.5,
            "weighted_cost_per_kg": 26.35,
            "value": 92.23,
        },
    ],
    "/inventory/adjustments": [
        {
            "id": 1,
            "location_type": "factory",
            "location_id": 0,
            "product_id": 1,
            "product_name": "Flour",
            "qty_delta_kg": -0.5,
            "reason": "Spillage during weighing",
            "status": "pending",
            "created_at": "2026-06-27T08:00:00",
        }
    ],
    "/transfer-exceptions": [],
    "/recipes": [
        {
            "id": 1,
            "finished_product_id": 3,
            "finished_code": "FG-BAKL",
            "finished_name": "Baklava Assorted",
            "items": [
                {
                    "ingredient_product_id": 1,
                    "ingredient_name": "Flour",
                    "ingredient_code": "RM-FLOUR",
                    "qty_per_kg_output": 0.45,
                },
                {
                    "ingredient_product_id": 2,
                    "ingredient_name": "Pistachio",
                    "ingredient_code": "RM-PIST",
                    "qty_per_kg_output": 0.25,
                },
            ],
        }
    ],
    "/auth/users": [
        {
            "id": 1,
            "username": "admin",
            "full_name": "Factory Manager",
            "role": "admin",
            "is_active": True,
        }
    ],
}

DEMO_REPORT_ROWS: dict[str, list[dict[str, object]]] = {
    "inventory-value": [
        {"category": "raw", "total_qty_kg": 58.5, "total_value": 72.3},
        {"category": "finished", "total_qty_kg": 10.7, "total_value": 127.68},
    ],
    "low-stock": [
        {
            "product_id": 1,
            "code": "RM-FLOUR",
            "name": "Flour",
            "quantity_kg": 8.5,
            "reorder_level": 10.0,
        }
    ],
    "production-yield": [
        {
            "batch_id": 1,
            "product": "Baklava Assorted",
            "target_kg": 12.0,
            "actual_kg": 11.7,
            "waste_kg": 0.3,
            "yield_pct": 97.5,
        }
    ],
    "transfer-exceptions": [],
}


def _page_href(route: str) -> str:
    filename = ROUTE_TO_FILE[route]
    return f"{BASE_PATH}/{filename}"


def rewrite_content(text: str) -> str:
    text = text.replace('href="/static/', f'href="{BASE_PATH}/static/')
    text = text.replace('src="/static/', f'src="{BASE_PATH}/static/')
    for route in ROUTE_TO_FILE:
        if route == "/":
            continue
        page_href = _page_href(route)
        text = text.replace(f'href="{route}"', f'href="{page_href}"')
        text = text.replace(f"href='{route}'", f"href='{page_href}'")
        text = text.replace(f'href: "{route}"', f'href: "{page_href}"')
        text = text.replace(
            f'window.location.href = "{route}"',
            f'window.location.href = "{page_href}"',
        )
    return text


def write_demo_mode_js() -> None:
    """Static GitHub Pages has no Python API — serve canned demo data instead."""
    payload = json.dumps(DEMO_GET_RESPONSES, indent=2)
    reports = json.dumps(DEMO_REPORT_ROWS, indent=2)
    js = f"""(function (global) {{
  global.BAKLAVA_DEMO = true;

  const DEMO_GET = {payload};
  const DEMO_REPORTS = {reports};

  function clone(value) {{
    return JSON.parse(JSON.stringify(value));
  }}

  function activateDemo() {{
    localStorage.setItem("baklava_access_token", "demo-token");
    localStorage.setItem("baklava_role", "admin");
    localStorage.setItem("baklava_username", "Demo User");

    if (!global.BaklavaApi || !global.BaklavaAuth) return;

    global.BaklavaApi.get = async function (path) {{
      if (Object.prototype.hasOwnProperty.call(DEMO_GET, path)) {{
        return clone(DEMO_GET[path]);
      }}
      if (path.startsWith("/reports/")) {{
        const reportType = path.split("/").pop();
        return {{
          report: reportType,
          rows: clone(DEMO_REPORTS[reportType] || []),
        }};
      }}
      return [];
    }};

    global.BaklavaApi.post = async function () {{
      throw new Error("Demo mode: saving is disabled. Run the FastAPI backend locally for full features.");
    }};

    global.BaklavaAuth.requireAuth = function () {{ return true; }};
    global.BaklavaAuth.isLoggedIn = function () {{ return true; }};
    global.BaklavaAuth.getUsername = function () {{ return "Demo User"; }};
    global.BaklavaAuth.getRole = function () {{ return "admin"; }};
    global.BaklavaAuth.login = async function () {{
      return {{ access_token: "demo-token", role: "admin" }};
    }};
    global.BaklavaAuth.logout = async function () {{
      window.location.href = "{_page_href("/dashboard")}";
    }};
  }}

  activateDemo();
}})(window);
"""
    (OUT_DIR / "static" / "js" / "demo_mode.js").write_text(js, encoding="utf-8")


def inject_demo_script(html: str) -> str:
    demo_tag = f'<script src="{BASE_PATH}/static/js/demo_mode.js"></script>'
    if demo_tag in html:
        return html
    return html.replace(
        '<script src="/static/js/shell.js"></script>',
        f'<script src="{BASE_PATH}/static/js/shell.js"></script>\n  {demo_tag}',
    ).replace(
        f'<script src="{BASE_PATH}/static/js/shell.js"></script>',
        f'<script src="{BASE_PATH}/static/js/shell.js"></script>\n  {demo_tag}',
    )


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    shutil.copytree(STATIC_ROOT / "css", OUT_DIR / "static" / "css")
    OUT_DIR.joinpath("static", "js").mkdir(parents=True)
    for js_file in (STATIC_ROOT / "js").glob("*.js"):
        content = rewrite_content(js_file.read_text(encoding="utf-8"))
        (OUT_DIR / "static" / "js" / js_file.name).write_text(content, encoding="utf-8")

    write_demo_mode_js()

    templates_dir = STATIC_ROOT / "templates"
    for template in templates_dir.glob("*.html"):
        if template.name.startswith("_") or template.parent.name == "partials":
            continue
        content = inject_demo_script(rewrite_content(template.read_text(encoding="utf-8")))
        (OUT_DIR / template.name).write_text(content, encoding="utf-8")

    index_content = inject_demo_script(
        rewrite_content((templates_dir / "dashboard.html").read_text(encoding="utf-8"))
    )
    (OUT_DIR / "index.html").write_text(index_content, encoding="utf-8")

    notice = """
<div style="margin:1rem auto;max-width:960px;padding:0.75rem 1rem;border-radius:8px;background:#eff6ff;border:1px solid #93c5fd;color:#1e40af;font-size:0.95rem;">
  <strong>Demo mode</strong> — sample factory data for presentation. Login is skipped.
  For real sign-in and live data, run the FastAPI backend locally (<code>uvicorn app.main:app --reload</code>).
</div>
"""
    for page in OUT_DIR.glob("*.html"):
        html = page.read_text(encoding="utf-8")
        html = html.replace("<body", notice + "<body", 1)
        page.write_text(html, encoding="utf-8")

    (OUT_DIR / ".nojekyll").touch()
    print(f"Built GitHub Pages site at {OUT_DIR}")


if __name__ == "__main__":
    main()
