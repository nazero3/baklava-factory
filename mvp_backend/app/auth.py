import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User, UserRole

JWT_ALGORITHM = "HS256"
LEGACY_SHA256_HEX_LEN = 64


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def is_legacy_sha256_hash(password_hash: str) -> bool:
    if len(password_hash) != LEGACY_SHA256_HEX_LEN:
        return False
    try:
        int(password_hash, 16)
        return True
    except ValueError:
        return False


def verify_password(password: str, password_hash: str) -> bool:
    if is_legacy_sha256_hash(password_hash):
        return hashlib.sha256(password.encode("utf-8")).hexdigest() == password_hash
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def migrate_password_hash_if_legacy(user: User, password: str) -> bool:
    if not is_legacy_sha256_hash(user.password_hash):
        return False
    if not verify_password(password, user.password_hash):
        return False
    user.password_hash = hash_password(password)
    return True


def issue_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def create_access_token(
    user: User,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value,
        "tv": user.token_version,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def invalidate_user_tokens(user: User) -> None:
    user.token_version += 1
    user.api_token = None


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.replace("Bearer ", "", 1).strip()
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("tv") != user.token_version:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def require_roles(*roles: UserRole):
    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return _check
