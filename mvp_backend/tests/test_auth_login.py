from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, is_legacy_sha256_hash
from app.models import User, UserRole


def test_login_success_returns_token_and_role(client: TestClient, admin_user: User):
    del admin_user
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "admin"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]
    assert isinstance(body["refresh_token"], str)
    assert body["refresh_token"]


def test_login_failure_wrong_password(client: TestClient, admin_user: User):
    del admin_user
    response = client.post("/auth/login", json={"username": "admin", "password": "wrong-password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_failure_unknown_user(client: TestClient, admin_user: User):
    del admin_user
    response = client.post("/auth/login", json={"username": "nobody", "password": "admin123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_protected_route_requires_bearer_token(client: TestClient, admin_user: User):
    del admin_user
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


def test_protected_route_rejects_invalid_token(client: TestClient, admin_user: User):
    del admin_user
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_protected_route_rejects_expired_token(client: TestClient, admin_user: User):
    expired = create_access_token(admin_user, expires_delta=timedelta(minutes=-5))
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired"


def test_protected_route_rejects_token_after_logout(client: TestClient, admin_headers: dict[str, str]):
    me_before = client.get("/auth/me", headers=admin_headers)
    assert me_before.status_code == 200

    logout = client.post("/auth/logout", headers=admin_headers)
    assert logout.status_code == 200

    me_after = client.get("/auth/me", headers=admin_headers)
    assert me_after.status_code == 401
    assert me_after.json()["detail"] == "Invalid token"


def test_refresh_token_issues_new_access_token(client: TestClient, admin_user: User):
    del admin_user
    login = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    refreshed = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    body = refreshed.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "admin"
    assert body["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200


def test_refresh_rejects_invalid_token(client: TestClient, admin_user: User):
    del admin_user
    response = client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_legacy_sha256_password_migrated_on_login(client: TestClient, db: Session):
    import hashlib

    legacy_hash = hashlib.sha256(b"admin123").hexdigest()
    user = User(
        username="legacy_admin",
        full_name="Legacy Admin",
        password_hash=legacy_hash,
        role=UserRole.admin,
        is_active=True,
    )
    db.add(user)
    db.commit()

    assert is_legacy_sha256_hash(legacy_hash)

    login = client.post("/auth/login", json={"username": "legacy_admin", "password": "admin123"})
    assert login.status_code == 200

    db.refresh(user)
    assert not is_legacy_sha256_hash(user.password_hash)


def test_protected_route_allows_valid_token(client: TestClient, admin_headers: dict[str, str]):
    response = client.get("/auth/me", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "admin"
    assert body["role"] == "admin"


def test_protected_route_enforces_role(client: TestClient, db: Session, admin_headers: dict[str, str]):
    store_manager = User(
        username="store1",
        full_name="Store Manager",
        password_hash=hash_password("store123"),
        role=UserRole.store_manager,
        is_active=True,
    )
    db.add(store_manager)
    db.commit()

    login = client.post("/auth/login", json={"username": "store1", "password": "store123"})
    assert login.status_code == 200
    store_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post(
        "/auth/users",
        json={
            "username": "new_user",
            "full_name": "New User",
            "password": "pass123",
            "role": "store_manager",
        },
        headers=store_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient role"

    me = client.get("/auth/me", headers=store_headers)
    assert me.status_code == 200
    assert me.json()["role"] == "store_manager"


def test_production_settings_disable_openapi():
    from app.config import Settings

    prod = Settings(env="production")
    assert prod.is_production
    assert (None if prod.is_production else "/docs") is None
