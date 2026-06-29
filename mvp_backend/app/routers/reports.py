from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_roles
from ..database import get_db
from ..models import TransferException, User, UserRole
from ..schemas import DashboardSummaryOut
from ..services import (
    dashboard_summary,
    low_stock_items,
    report_inventory_value,
    report_production_yield,
)

router = APIRouter(tags=["reports"])


@router.get("/dashboard/daily-summary", response_model=DashboardSummaryOut)
def get_daily_summary(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return dashboard_summary(db)


@router.get("/reports/{report_type}")
def get_report(
    report_type: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.factory_manager,
            UserRole.accountant,
            UserRole.executive,
            UserRole.production_supervisor,
        )
    ),
):
    if report_type == "inventory-value":
        return {"report": report_type, "rows": report_inventory_value(db)}
    if report_type == "low-stock":
        return {"report": report_type, "rows": low_stock_items(db)}
    if report_type == "transfer-exceptions":
        rows = db.scalars(
            select(TransferException)
            .order_by(TransferException.id.desc())
            .offset(skip)
            .limit(limit)
        ).all()
        return {
            "report": report_type,
            "rows": [
                {
                    "id": e.id,
                    "transfer_id": e.transfer_id,
                    "expected_qty_kg": round(e.expected_qty_kg, 3),
                    "received_qty_kg": round(e.received_qty_kg, 3),
                    "difference_qty_kg": round(e.difference_qty_kg, 3),
                    "status": e.status,
                }
                for e in rows
            ],
        }
    if report_type == "production-yield":
        return {
            "report": report_type,
            "rows": report_production_yield(db, skip=skip, limit=limit),
        }
    raise HTTPException(status_code=404, detail="Unknown report type")
