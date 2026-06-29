#!/usr/bin/env python3
"""Build a static GitHub Pages preview of the ERP web UI."""
from __future__ import annotations

import shutil
from pathlib import Path

BASE_PATH = "/manbaj-factory"
REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = REPO_ROOT / "mvp_backend" / "app" / "static"
OUT_DIR = REPO_ROOT / "github-pages"

ROUTE_TO_FILE = {
    "/": "login.html",
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


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    shutil.copytree(STATIC_ROOT / "css", OUT_DIR / "static" / "css")
    OUT_DIR.joinpath("static", "js").mkdir(parents=True)
    for js_file in (STATIC_ROOT / "js").glob("*.js"):
        content = rewrite_content(js_file.read_text(encoding="utf-8"))
        (OUT_DIR / "static" / "js" / js_file.name).write_text(content, encoding="utf-8")

    templates_dir = STATIC_ROOT / "templates"
    for template in templates_dir.glob("*.html"):
        if template.name.startswith("_") or template.parent.name == "partials":
            continue
        content = rewrite_content(template.read_text(encoding="utf-8"))
        (OUT_DIR / template.name).write_text(content, encoding="utf-8")

    index_content = rewrite_content((templates_dir / "login.html").read_text(encoding="utf-8"))
    (OUT_DIR / "index.html").write_text(index_content, encoding="utf-8")

    notice = """
<div style="margin:1rem auto;max-width:720px;padding:0.75rem 1rem;border-radius:8px;background:#fff7ed;border:1px solid #fdba74;color:#9a3412;font-size:0.95rem;">
  UI preview only. Sign-in and live data require deploying the FastAPI backend from the README.
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
