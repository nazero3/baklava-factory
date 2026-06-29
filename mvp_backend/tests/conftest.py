"""
Receiving tests: request receiving_supplier, receiving_raw_product, 
receiving_headers, client fixtures.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_mvp.db")
os.environ.setdefault("ENV", "development")
os.environ["BOOTSTRAP_ADMIN"] = ""

from app.auth import create_access_token, hash_password  # noqa: E402
from app.database import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User, UserRole, Supplier, Product, ProductCategory  # noqa: E402


@pytest.fixture
def db() -> Session:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db: Session) -> TestClient:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db: Session) -> User:
    user = User(
        username="admin",
        full_name="System Administrator",
        password_hash=hash_password("admin123"),
        role=UserRole.admin,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_headers(client: TestClient, admin_user: User) -> dict[str, str]:
    """Auth headers via token-based auth (no /auth/login HTTP round-trip needed)."""
    token = create_access_token(admin_user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def receiving_headers(admin_user: User) -> dict[str, str]:
    """Auth headers for receiving tests without /auth/login HTTP round-trip."""
    token = create_access_token(admin_user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def receiving_supplier(db: Session) -> Supplier:
    """Create a supplier fixture for receiving tests."""
    row = Supplier(name="Receiving Test Supplier")
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@pytest.fixture
def receiving_raw_product(db: Session) -> Product:
    """Create a raw product fixture for receiving tests."""
    row = Product(
        code="RM-RECV-TEST",
        name="Receiving Test Flour",
        category=ProductCategory.raw,
        unit="kg",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
