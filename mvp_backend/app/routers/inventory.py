from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..database import get_db
from ..models import Inventory, InventoryAdjustment, LocationType, Product, Store, User, UserRole
from ..schemas import (
    AdjustmentActionOut,
    InventoryAdjustmentCreate,
    InventoryAdjustmentOut,
    InventoryOut,
)
from ..services import (
    approve_inventory_adjustment,
    create_inventory_adjustment,
    reject_inventory_adjustment,
)

router = APIRouter(tags=["inventory"])


@router.get("/inventory", response_model=list[InventoryOut])
def list_inventory(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.factory_manager,
            UserRole.accountant,
            UserRole.executive,
            UserRole.warehouse,
            UserRole.production_supervisor,
        )
    ),
):
    products = {p.id: p for p in db.scalars(select(Product)).all()}
    stores = {s.id: s.name for s in db.execute(select(Store.id, Store.name)).all()}
    rows = db.scalars(select(Inventory).offset(skip).limit(limit)).all()
    result = []
    for r in rows:
        product = products.get(r.product_id)
        location_name = (
            "Factory"
            if r.location_type == LocationType.factory
            else stores.get(r.location_id, f"Store #{r.location_id}")
        )
        result.append(
            {
                "location_type": r.location_type,
                "location_id": r.location_id,
                "location_name": location_name,
                "product_id": r.product_id,
                "product_code": product.code if product else None,
                "product_name": product.name if product else None,
                "quantity_kg": round(r.quantity_kg, 3),
                "weighted_cost_per_kg": round(r.weighted_cost_per_kg, 3),
                "value": round(r.quantity_kg * r.weighted_cost_per_kg, 2),
            }
        )
    return result


@router.post("/inventory/adjustments", response_model=AdjustmentActionOut)
def request_inventory_adjustment(
    payload: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)
    ),
):
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        adjustment = create_inventory_adjustment(
            db=db,
            location_type=payload.location_type,
            location_id=payload.location_id,
            product_id=payload.product_id,
            qty_delta_kg=payload.qty_delta_kg,
            reason=payload.reason,
            requested_by_user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(adjustment)
    return {"adjustment_id": adjustment.id, "status": adjustment.status}


@router.post(
    "/inventory/adjustments/{adjustment_id}/approve", response_model=AdjustmentActionOut
)
def approve_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager)),
):
    adjustment = db.get(InventoryAdjustment, adjustment_id)
    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found")
    try:
        approve_inventory_adjustment(db, adjustment, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(adjustment)
    return {"adjustment_id": adjustment.id, "status": adjustment.status}


@router.post(
    "/inventory/adjustments/{adjustment_id}/reject", response_model=AdjustmentActionOut
)
def reject_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager)),
):
    adjustment = db.get(InventoryAdjustment, adjustment_id)
    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found")
    try:
        reject_inventory_adjustment(db, adjustment, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(adjustment)
    return {"adjustment_id": adjustment.id, "status": adjustment.status}


@router.get("/inventory/adjustments", response_model=list[InventoryAdjustmentOut])
def list_adjustments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)
    ),
):
    products = {p.id: p.name for p in db.execute(select(Product.id, Product.name)).all()}
    rows = db.scalars(
        select(InventoryAdjustment)
        .order_by(InventoryAdjustment.id.desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return [
        {
            "id": a.id,
            "location_type": a.location_type,
            "location_id": a.location_id,
            "product_id": a.product_id,
            "product_name": products.get(a.product_id),
            "qty_delta_kg": round(a.qty_delta_kg, 3),
            "reason": a.reason,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in rows
    ]
