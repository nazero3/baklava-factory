from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..database import get_db
from ..models import Product, Store, StoreMovement, User, UserRole
from ..schemas import StoreCreate, StoreMovementCreate, StoreMovementOut, StoreOut
from ..services import apply_store_movement

router = APIRouter(tags=["stores"])


@router.get("/stores/list", response_model=list[StoreOut])
def list_stores(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.factory_manager,
            UserRole.warehouse,
            UserRole.store_manager,
        )
    ),
):
    return db.scalars(select(Store).order_by(Store.id).offset(skip).limit(limit)).all()


@router.post("/stores", response_model=StoreOut)
def create_store(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager)),
):
    existing = db.scalar(select(Store).where(Store.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="Store name already exists")
    row = Store(name=payload.name)
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Store name already exists") from exc
    db.refresh(row)
    return row


@router.post("/stores/{store_id}/movements", response_model=StoreMovementOut)
def add_store_movement(
    store_id: int,
    payload: StoreMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.store_manager)
    ),
):
    store = db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    row = StoreMovement(
        store_id=store_id,
        created_by_user_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(row)
    db.flush()
    try:
        apply_store_movement(db, row)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "store_id": row.store_id,
        "store_name": store.name,
        "product_id": row.product_id,
        "product_name": product.name,
        "movement_type": row.movement_type,
        "qty_kg": round(row.qty_kg, 3),
        "unit_price": round(row.unit_price, 3),
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/store-movements", response_model=list[StoreMovementOut])
def list_store_movements(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.store_manager)
    ),
):
    products = {p.id: p.name for p in db.execute(select(Product.id, Product.name)).all()}
    stores = {s.id: s.name for s in db.execute(select(Store.id, Store.name)).all()}
    rows = db.scalars(
        select(StoreMovement).order_by(StoreMovement.id.desc()).offset(skip).limit(limit)
    ).all()
    return [
        {
            "id": m.id,
            "store_id": m.store_id,
            "store_name": stores.get(m.store_id),
            "product_id": m.product_id,
            "product_name": products.get(m.product_id),
            "movement_type": m.movement_type,
            "qty_kg": round(m.qty_kg, 3),
            "unit_price": round(m.unit_price, 3),
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in rows
    ]
