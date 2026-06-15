import csv
import io
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import get_current_user, hash_password, issue_token, require_roles, verify_password
from .database import Base, SessionLocal, engine, get_db
from .models import (
    Inventory,
    InventoryAdjustment,
    LocationType,
    MovementType,
    Product,
    ProductCategory,
    ProductionBatch,
    Recipe,
    RecipeItem,
    Receiving,
    Store,
    StoreMovement,
    Supplier,
    Transfer,
    TransferException,
    User,
    UserRole,
)
from .schemas import (
    InventoryAdjustmentCreate,
    LoginRequest,
    ProductCreate,
    ProductionComplete,
    RecipeCreate,
    ReceivingCreate,
    StoreCreate,
    StoreMovementCreate,
    SupplierCreate,
    TransferDispatch,
    TransferReceive,
    UserCreate,
)
from .services import (
    approve_inventory_adjustment,
    approve_transfer_exception,
    apply_receiving,
    apply_store_movement,
    create_inventory_adjustment,
    dashboard_summary,
    dispatch_transfer,
    receive_transfer,
    consume_for_production,
    post_finished_goods,
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing_admin = db.scalar(select(User).where(User.username == "admin"))
        if not existing_admin:
            db.add(
                User(
                    username="admin",
                    full_name="System Administrator",
                    password_hash=hash_password("admin123"),
                    role=UserRole.admin,
                    is_active=True,
                )
            )
            db.commit()
    yield


app = FastAPI(title="Baklava Factory MVP API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username, User.is_active.is_(True)))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = issue_token()
    user.api_token = token
    db.commit()
    return {"access_token": token, "token_type": "bearer", "role": user.role}


@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "full_name": current_user.full_name, "role": current_user.role}


@app.post("/auth/users")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "role": user.role}


@app.post("/suppliers")
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)),
):
    row = Supplier(name=payload.name)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/stores")
def create_store(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager)),
):
    row = Store(name=payload.name)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/products")
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.accountant)),
):
    row = Product(code=payload.code, name=payload.name, category=payload.category, unit=payload.unit)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/recipes")
def create_recipe(
    payload: RecipeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.production_supervisor)),
):
    finished = db.get(Product, payload.finished_product_id)
    if not finished:
        raise HTTPException(status_code=404, detail="Finished product not found")
    recipe = Recipe(finished_product_id=payload.finished_product_id)
    db.add(recipe)
    db.flush()
    for item in payload.items:
        ingredient = db.get(Product, item.ingredient_product_id)
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient {item.ingredient_product_id} not found")
        db.add(
            RecipeItem(
                recipe_id=recipe.id,
                ingredient_product_id=item.ingredient_product_id,
                qty_per_kg_output=item.qty_per_kg_output,
            )
        )
    db.commit()
    return {"recipe_id": recipe.id, "item_count": len(payload.items)}


@app.post("/receivings")
def create_receiving(
    payload: ReceivingCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)),
):
    if not db.get(Supplier, payload.supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    row = Receiving(**payload.model_dump())
    db.add(row)
    db.flush()
    apply_receiving(db, row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/production/batches/complete")
def complete_batch(
    payload: ProductionComplete,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.production_supervisor)),
):
    if not db.get(Product, payload.finished_product_id):
        raise HTTPException(status_code=404, detail="Finished product not found")
    try:
        consumed_cost, consumed_rows = consume_for_production(db, payload.finished_product_id, payload.actual_kg)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    batch = ProductionBatch(**payload.model_dump())
    db.add(batch)
    post_finished_goods(db, payload.finished_product_id, payload.actual_kg, consumed_cost)
    db.commit()
    db.refresh(batch)
    return {"batch_id": batch.id, "consumed": consumed_rows}


@app.post("/transfers/dispatch")
def transfer_dispatch(
    payload: TransferDispatch,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)),
):
    if not db.get(Store, payload.to_store_id):
        raise HTTPException(status_code=404, detail="Store not found")
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    row = Transfer(**payload.model_dump())
    db.add(row)
    db.flush()
    try:
        dispatch_transfer(db, row)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(row)
    return row


@app.post("/transfers/{transfer_id}/receive")
def transfer_receive(
    transfer_id: int,
    payload: TransferReceive,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.store_manager)),
):
    row = db.get(Transfer, transfer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Transfer not found")
    try:
        receive_transfer(db, row, payload.received_qty_kg, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(row)
    return row


@app.post("/stores/{store_id}/movements")
def add_store_movement(
    store_id: int,
    payload: StoreMovementCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.store_manager)),
):
    if not db.get(Store, store_id):
        raise HTTPException(status_code=404, detail="Store not found")
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    row = StoreMovement(store_id=store_id, **payload.model_dump())
    db.add(row)
    db.flush()
    try:
        apply_store_movement(db, row)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(row)
    return row


@app.post("/inventory/adjustments")
def request_inventory_adjustment(
    payload: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.warehouse)),
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


@app.post("/inventory/adjustments/{adjustment_id}/approve")
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


@app.post("/transfer-exceptions/{exception_id}/approve")
def approve_exception(
    exception_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager)),
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


@app.get("/inventory")
def list_inventory(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.accountant, UserRole.executive)),
):
    rows = db.scalars(select(Inventory)).all()
    return [
        {
            "location_type": r.location_type,
            "location_id": r.location_id,
            "product_id": r.product_id,
            "quantity_kg": round(r.quantity_kg, 3),
            "weighted_cost_per_kg": round(r.weighted_cost_per_kg, 3),
        }
        for r in rows
    ]


@app.get("/dashboard/daily-summary")
def get_daily_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.accountant, UserRole.executive)),
):
    return dashboard_summary(db)


@app.post("/import/products-csv")
async def import_products_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager)),
):
    raw = (await file.read()).decode("utf-8")
    reader = csv.DictReader(io.StringIO(raw))
    imported = 0
    for row in reader:
        code = row.get("code", "").strip()
        name = row.get("name", "").strip()
        category = row.get("category", "").strip()
        unit = row.get("unit", "kg").strip() or "kg"
        if not code or not name or not category:
            continue
        existing = db.scalar(select(Product).where(Product.code == code))
        if existing:
            existing.name = name
            existing.category = ProductCategory(category)
            existing.unit = unit
        else:
            db.add(Product(code=code, name=name, category=ProductCategory(category), unit=unit))
        imported += 1
    db.commit()
    return {"imported_rows": imported}


@app.post("/import/store-movements-csv")
async def import_store_movements_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.store_manager)),
):
    raw = (await file.read()).decode("utf-8")
    reader = csv.DictReader(io.StringIO(raw))
    imported = 0
    for row in reader:
        store_id = int(row.get("store_id", "0"))
        product_id = int(row.get("product_id", "0"))
        movement_type = row.get("movement_type", "").strip()
        qty_kg = float(row.get("qty_kg", "0"))
        if not store_id or not product_id or qty_kg <= 0:
            continue
        movement = StoreMovement(
            store_id=store_id,
            product_id=product_id,
            movement_type=MovementType(movement_type),
            qty_kg=qty_kg,
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


@app.get("/export/products-csv")
def export_products_csv(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.accountant, UserRole.executive)),
):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "code", "name", "category", "unit"])
    for product in db.scalars(select(Product)).all():
        writer.writerow([product.id, product.code, product.name, product.category, product.unit])
    return PlainTextResponse(output.getvalue(), media_type="text/csv")


@app.get("/export/daily-summary-csv")
def export_daily_summary_csv(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.factory_manager, UserRole.accountant, UserRole.executive)),
):
    summary = dashboard_summary(db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    for key, value in summary.items():
        writer.writerow([key, value])
    return PlainTextResponse(output.getvalue(), media_type="text/csv")
