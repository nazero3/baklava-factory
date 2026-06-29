import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..config import settings
from ..database import get_db
from ..models import MovementType, Product, ProductCategory, StoreMovement, User, UserRole
from ..schemas import ImportResultOut
from ..services import apply_store_movement, dashboard_summary

router = APIRouter(tags=["imports"])


async def _read_csv_bytes(file: UploadFile) -> str:
    """Read upload enforcing the configured size limit."""
    max_bytes = settings.max_csv_upload_bytes
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"CSV file too large. Maximum allowed size is {max_bytes // 1024 // 1024} MB.",
        )
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded.") from exc


@router.post("/import/products-csv", response_model=ImportResultOut)
async def import_products_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager)),
):
    raw = await _read_csv_bytes(file)
    reader = csv.DictReader(io.StringIO(raw))
    imported = 0
    for row in reader:
        code = row.get("code", "").strip()
        name = row.get("name", "").strip()
        category_str = row.get("category", "").strip()
        unit = row.get("unit", "kg").strip() or "kg"
        if not code or not name or not category_str:
            continue
        try:
            category = ProductCategory(category_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category value {category_str!r}. Must be 'raw' or 'finished'.",
            )
        existing = db.scalar(select(Product).where(Product.code == code))
        if existing:
            existing.name = name
            existing.category = category
            existing.unit = unit
        else:
            db.add(Product(code=code, name=name, category=category, unit=unit))
        imported += 1
    db.commit()
    return {"imported_rows": imported}


@router.post("/import/store-movements-csv", response_model=ImportResultOut)
async def import_store_movements_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.admin, UserRole.factory_manager, UserRole.store_manager)
    ),
):
    raw = await _read_csv_bytes(file)
    reader = csv.DictReader(io.StringIO(raw))
    imported = 0
    for row in reader:
        try:
            store_id = int(row.get("store_id", "0"))
            product_id = int(row.get("product_id", "0"))
            qty_kg = float(row.get("qty_kg", "0"))
        except (ValueError, TypeError):
            continue
        movement_type_str = row.get("movement_type", "").strip()
        if not store_id or not product_id or qty_kg <= 0 or not movement_type_str:
            continue
        try:
            movement_type = MovementType(movement_type_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid movement_type value {movement_type_str!r}.",
            )
        unit_price = float(row.get("unit_price", "0") or "0")
        movement = StoreMovement(
            store_id=store_id,
            product_id=product_id,
            movement_type=movement_type,
            qty_kg=qty_kg,
            unit_price=unit_price,
            created_by_user_id=current_user.id,
        )
        db.add(movement)
        db.flush()
        try:
            apply_store_movement(db, movement)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        imported += 1
    db.commit()
    return {"imported_rows": imported}


@router.get("/export/products-csv")
def export_products_csv(
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.factory_manager,
            UserRole.accountant,
            UserRole.executive,
        )
    ),
):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "code", "name", "category", "unit"])
    for product in db.scalars(select(Product)).all():
        writer.writerow(
            [product.id, product.code, product.name, product.category, product.unit]
        )
    return PlainTextResponse(output.getvalue(), media_type="text/csv")


@router.get("/export/daily-summary-csv")
def export_daily_summary_csv(
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.factory_manager,
            UserRole.accountant,
            UserRole.executive,
        )
    ),
):
    summary = dashboard_summary(db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    for key, value in summary.items():
        if not isinstance(value, (list, dict)):
            writer.writerow([key, value])
    return PlainTextResponse(output.getvalue(), media_type="text/csv")
