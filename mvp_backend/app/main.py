from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .auth import hash_password
from .config import settings
from .database import SessionLocal, get_db
from .limiter import limiter
from .logging_config import configure_logging
from .migrations import ensure_database_schema
from .models import User, UserRole
from .request_logging import RequestLoggingMiddleware
from .routers import auth, imports, inventory, production, products, receivings, reports, stores, suppliers, transfers


def _maybe_bootstrap_admin(db: Session) -> None:
    if not settings.bootstrap_admin:
        return
    username, _, password = settings.bootstrap_admin.partition(":")
    username = username.strip()
    password = password.strip()
    if not username or not password:
        return
    existing = db.scalar(select(User).where(User.username == username))
    if existing:
        return
    db.add(
        User(
            username=username,
            full_name="Bootstrap Administrator",
            password_hash=hash_password(password),
            role=UserRole.admin,
            is_active=True,
        )
    )
    db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(production=settings.is_production)
    ensure_database_schema()
    with SessionLocal() as db:
        _maybe_bootstrap_admin(db)
    yield


app = FastAPI(
    title="Baklava Factory ERP API",
    version="0.2.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestLoggingMiddleware)
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = STATIC_DIR / "templates"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- API routers ---
app.include_router(auth.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(receivings.router)
app.include_router(production.router)
app.include_router(transfers.router)
app.include_router(stores.router)
app.include_router(inventory.router)
app.include_router(reports.router)
app.include_router(imports.router)


# --- health ---

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok", "database": "reachable"}


# --- UI page routes ---

def _page(name: str) -> FileResponse:
    return FileResponse(TEMPLATES_DIR / name)


@app.get("/", include_in_schema=False)
def root_ui():
    return RedirectResponse("/login", status_code=302)


@app.get("/login", include_in_schema=False)
def login_ui():
    return _page("login.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard_ui():
    return _page("dashboard.html")


@app.get("/suppliers", include_in_schema=False)
def supplier_ui():
    return _page("supplier.html")


@app.get("/stores", include_in_schema=False)
def stores_ui():
    return _page("stores.html")


@app.get("/products-view", include_in_schema=False)
def products_ui():
    return _page("products.html")


@app.get("/recipes-view", include_in_schema=False)
def recipes_ui():
    return _page("recipes.html")


@app.get("/receiving", include_in_schema=False)
def receiving_ui():
    return _page("receiving.html")


@app.get("/production", include_in_schema=False)
def production_ui():
    return _page("production.html")


@app.get("/dispatch", include_in_schema=False)
def dispatch_ui():
    return _page("dispatch.html")


@app.get("/store-return", include_in_schema=False)
def store_return_ui():
    return _page("store-return.html")


@app.get("/inventory-view", include_in_schema=False)
def inventory_ui():
    return _page("inventory.html")


@app.get("/approvals", include_in_schema=False)
def approvals_ui():
    return _page("approvals.html")


@app.get("/reports", include_in_schema=False)
def reports_ui():
    return _page("reports.html")


@app.get("/users", include_in_schema=False)
def users_ui():
    return _page("users.html")
