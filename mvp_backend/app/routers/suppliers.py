from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..database import get_db
from ..models import Supplier, User, UserRole
from ..schemas import SupplierCreate, SupplierOut

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("/list", response_model=list[SupplierOut])
def list_suppliers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)
    ),
):
    return db.scalars(select(Supplier).order_by(Supplier.id).offset(skip).limit(limit)).all()


@router.post("", response_model=SupplierOut)
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)
    ),
):
    existing = db.scalar(select(Supplier).where(Supplier.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="Supplier name already exists")
    row = Supplier(name=payload.name)
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Supplier name already exists") from exc
    db.refresh(row)
    return row
