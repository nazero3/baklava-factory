from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..database import get_db
from ..models import Product, Receiving, Supplier, User, UserRole
from ..schemas import ReceivingCreate, ReceivingOut
from ..services import apply_receiving

router = APIRouter(tags=["receivings"])


@router.post("/receivings", response_model=ReceivingOut)
def create_receiving(
    payload: ReceivingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)
    ),
):
    if not db.get(Supplier, payload.supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    row = Receiving(**payload.model_dump(), created_by_user_id=current_user.id)
    db.add(row)
    db.flush()
    apply_receiving(db, row)
    db.commit()
    db.refresh(row)
    # Enrich with names for the response
    supplier = db.get(Supplier, row.supplier_id)
    product = db.get(Product, row.product_id)
    return {
        "id": row.id,
        "supplier_id": row.supplier_id,
        "supplier_name": supplier.name if supplier else None,
        "product_id": row.product_id,
        "product_name": product.name if product else None,
        "qty_kg": round(row.qty_kg, 3),
        "unit_cost": round(row.unit_cost, 3),
        "lot_no": row.lot_no,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/receivings", response_model=list[ReceivingOut])
def list_receivings(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)
    ),
):
    products = {p.id: p.name for p in db.execute(select(Product.id, Product.name)).all()}
    suppliers = {s.id: s.name for s in db.execute(select(Supplier.id, Supplier.name)).all()}
    rows = db.scalars(
        select(Receiving).order_by(Receiving.id.desc()).offset(skip).limit(limit)
    ).all()
    return [
        {
            "id": r.id,
            "supplier_id": r.supplier_id,
            "supplier_name": suppliers.get(r.supplier_id),
            "product_id": r.product_id,
            "product_name": products.get(r.product_id),
            "qty_kg": round(r.qty_kg, 3),
            "unit_cost": round(r.unit_cost, 3),
            "lot_no": r.lot_no,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
