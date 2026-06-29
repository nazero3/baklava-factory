from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..database import get_db
from ..models import Product, Store, Transfer, TransferException, User, UserRole
from ..schemas import (
    ExceptionActionOut,
    TransferDispatch,
    TransferExceptionOut,
    TransferOut,
    TransferReceive,
)
from ..services import (
    approve_transfer_exception,
    dispatch_transfer,
    receive_transfer,
    reject_transfer_exception,
)

router = APIRouter(tags=["transfers"])


@router.post("/transfers/dispatch", response_model=TransferOut)
def transfer_dispatch(
    payload: TransferDispatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)
    ),
):
    if not db.get(Store, payload.to_store_id):
        raise HTTPException(status_code=404, detail="Store not found")
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    row = Transfer(**payload.model_dump(), created_by_user_id=current_user.id)
    db.add(row)
    db.flush()
    try:
        dispatch_transfer(db, row)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(row)
    store = db.get(Store, row.to_store_id)
    product = db.get(Product, row.product_id)
    return {
        "id": row.id,
        "product_id": row.product_id,
        "product_name": product.name if product else None,
        "qty_kg": round(row.qty_kg, 3),
        "to_store_id": row.to_store_id,
        "to_store_name": store.name if store else None,
        "status": row.status,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.post("/transfers/{transfer_id}/receive", response_model=TransferOut)
def transfer_receive(
    transfer_id: int,
    payload: TransferReceive,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.store_manager)
    ),
):
    # Lock the row to prevent concurrent double-receives on PostgreSQL
    row = db.scalar(select(Transfer).where(Transfer.id == transfer_id).with_for_update())
    if not row:
        raise HTTPException(status_code=404, detail="Transfer not found")
    try:
        receive_transfer(db, row, payload.received_qty_kg, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(row)
    store = db.get(Store, row.to_store_id)
    product = db.get(Product, row.product_id)
    return {
        "id": row.id,
        "product_id": row.product_id,
        "product_name": product.name if product else None,
        "qty_kg": round(row.qty_kg, 3),
        "to_store_id": row.to_store_id,
        "to_store_name": store.name if store else None,
        "status": row.status,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/transfers", response_model=list[TransferOut])
def list_transfers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
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
    products = {p.id: p.name for p in db.execute(select(Product.id, Product.name)).all()}
    stores = {s.id: s.name for s in db.execute(select(Store.id, Store.name)).all()}
    rows = db.scalars(
        select(Transfer).order_by(Transfer.id.desc()).offset(skip).limit(limit)
    ).all()
    return [
        {
            "id": tr.id,
            "product_id": tr.product_id,
            "product_name": products.get(tr.product_id),
            "qty_kg": round(tr.qty_kg, 3),
            "to_store_id": tr.to_store_id,
            "to_store_name": stores.get(tr.to_store_id),
            "status": tr.status,
            "created_at": tr.created_at.isoformat() if tr.created_at else None,
        }
        for tr in rows
    ]


@router.post(
    "/transfer-exceptions/{exception_id}/approve", response_model=ExceptionActionOut
)
def approve_exception(
    exception_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager)
    ),
):
    transfer_exception = db.get(TransferException, exception_id)
    if not transfer_exception:
        raise HTTPException(status_code=404, detail="Transfer exception not found")
    try:
        approve_transfer_exception(db, transfer_exception, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(transfer_exception)
    return {"exception_id": transfer_exception.id, "status": transfer_exception.status}


@router.post(
    "/transfer-exceptions/{exception_id}/reject", response_model=ExceptionActionOut
)
def reject_exception(
    exception_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager)
    ),
):
    transfer_exception = db.get(TransferException, exception_id)
    if not transfer_exception:
        raise HTTPException(status_code=404, detail="Transfer exception not found")
    try:
        reject_transfer_exception(db, transfer_exception, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(transfer_exception)
    return {"exception_id": transfer_exception.id, "status": transfer_exception.status}


@router.get("/transfer-exceptions", response_model=list[TransferExceptionOut])
def list_exceptions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager)),
):
    rows = db.scalars(
        select(TransferException).order_by(TransferException.id.desc()).offset(skip).limit(limit)
    ).all()
    return [
        {
            "id": e.id,
            "transfer_id": e.transfer_id,
            "expected_qty_kg": round(e.expected_qty_kg, 3),
            "received_qty_kg": round(e.received_qty_kg, 3),
            "difference_qty_kg": round(e.difference_qty_kg, 3),
            "status": e.status,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in rows
    ]
