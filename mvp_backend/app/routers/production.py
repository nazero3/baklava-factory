from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..database import get_db
from ..models import Product, ProductionBatch, User, UserRole
from ..schemas import BatchCreateOut, ProductionBatchOut, ProductionComplete
from ..services import consume_for_production, post_finished_goods

router = APIRouter(tags=["production"])


@router.post("/production/batches/complete", response_model=BatchCreateOut)
def complete_batch(
    payload: ProductionComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.admin, UserRole.factory_manager, UserRole.production_supervisor
        )
    ),
):
    if not db.get(Product, payload.finished_product_id):
        raise HTTPException(status_code=404, detail="Finished product not found")
    try:
        consumed_cost, consumed_rows = consume_for_production(
            db, payload.finished_product_id, payload.actual_kg
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    batch = ProductionBatch(**payload.model_dump(), created_by_user_id=current_user.id)
    db.add(batch)
    post_finished_goods(db, payload.finished_product_id, payload.actual_kg, consumed_cost)
    db.commit()
    db.refresh(batch)
    return {"batch_id": batch.id, "consumed": consumed_rows}


@router.get("/production/batches", response_model=list[ProductionBatchOut])
def list_batches(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin, UserRole.factory_manager, UserRole.production_supervisor
        )
    ),
):
    products = {p.id: p.name for p in db.execute(select(Product.id, Product.name)).all()}
    rows = db.scalars(
        select(ProductionBatch).order_by(ProductionBatch.id.desc()).offset(skip).limit(limit)
    ).all()
    return [
        {
            "id": b.id,
            "finished_product_id": b.finished_product_id,
            "finished_name": products.get(b.finished_product_id),
            "target_kg": round(b.target_kg, 3),
            "actual_kg": round(b.actual_kg, 3),
            "waste_kg": round(b.waste_kg, 3),
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in rows
    ]
