from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    get_current_user,
    hash_password,
    invalidate_user_tokens,
    issue_refresh_token,
    migrate_password_hash_if_legacy,
    require_roles,
    verify_password,
)
from ..config import settings
from ..database import get_db
from ..limiter import limiter
from ..models import User, UserRole
from ..schemas import LoginRequest, RefreshRequest, UserCreate, UserOut

router = APIRouter(tags=["auth"])


def _is_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return False
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)


@router.post("/auth/login")
@limiter.limit(settings.login_rate_limit)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(
        select(User).where(User.username == payload.username, User.is_active.is_(True))
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    migrate_password_hash_if_legacy(user, payload.password)
    refresh_token = issue_refresh_token()
    user.api_token = refresh_token
    user.api_token_expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    access_token = create_access_token(user)
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",  # nosec B105
        "role": user.role,
    }


@router.post("/auth/refresh")
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    user = db.scalar(
        select(User).where(User.api_token == payload.refresh_token, User.is_active.is_(True))
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if _is_expired(user.api_token_expires_at):
        invalidate_user_tokens(user)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",  # nosec B105
        "role": user.role,
    }


@router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.get(User, current_user.id)
    if user:
        invalidate_user_tokens(user)
        db.commit()
    return {"status": "logged_out"}  # nosec B105


@router.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }


@router.post("/auth/users", response_model=UserOut)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists") from exc
    db.refresh(user)
    return user


@router.get("/auth/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    return db.scalars(select(User).order_by(User.id)).all()
