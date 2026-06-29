from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .constants import FACTORY_LOCATION_ID
from .models import (
    ApprovalStatus,
    Inventory,
    InventoryAdjustment,
    LocationType,
    MovementType,
    Product,
    ProductCategory,
    ProductionBatch,
    Recipe,
    Receiving,
    StoreMovement,
    Transfer,
    TransferException,
    TransferStatus,
)


def inventory_slot(db: Session, location_type: LocationType, location_id: int, product_id: int) -> Inventory:
    slot = db.scalar(
        select(Inventory).where(
            Inventory.location_type == location_type,
            Inventory.location_id == location_id,
            Inventory.product_id == product_id,
        )
    )
    if not slot:
        slot = Inventory(
            location_type=location_type,
            location_id=location_id,
            product_id=product_id,
            quantity_kg=0,
            weighted_cost_per_kg=0,
        )
        db.add(slot)
        db.flush()
    return slot


def apply_receiving(db: Session, receiving: Receiving) -> None:
    slot = inventory_slot(db, LocationType.factory, FACTORY_LOCATION_ID, receiving.product_id)
    new_total_qty = slot.quantity_kg + receiving.qty_kg
    if new_total_qty <= 0:
        return
    slot.weighted_cost_per_kg = (
        (slot.quantity_kg * slot.weighted_cost_per_kg) + (receiving.qty_kg * receiving.unit_cost)
    ) / new_total_qty
    slot.quantity_kg = new_total_qty


def consume_for_production(
    db: Session, finished_product_id: int, actual_kg: float
) -> tuple[float, list[dict]]:
    recipe = db.scalar(
        select(Recipe)
        .where(Recipe.finished_product_id == finished_product_id)
        .options(selectinload(Recipe.items))
    )
    if not recipe:
        raise ValueError("No recipe found for finished product")

    consumed_cost = 0.0
    consumed_rows = []
    for item in recipe.items:
        qty_needed = item.qty_per_kg_output * actual_kg
        raw_slot = inventory_slot(db, LocationType.factory, FACTORY_LOCATION_ID, item.ingredient_product_id)
        if raw_slot.quantity_kg < qty_needed:
            raise ValueError("Insufficient raw material for production")
        raw_slot.quantity_kg -= qty_needed
        consumed_cost += qty_needed * raw_slot.weighted_cost_per_kg
        consumed_rows.append({"ingredient_product_id": item.ingredient_product_id, "qty_kg": qty_needed})
    return consumed_cost, consumed_rows


def post_finished_goods(
    db: Session, finished_product_id: int, actual_kg: float, total_cost: float
) -> None:
    slot = inventory_slot(db, LocationType.factory, FACTORY_LOCATION_ID, finished_product_id)
    new_total_qty = slot.quantity_kg + actual_kg
    if new_total_qty <= 0:
        return
    new_cost = total_cost / actual_kg if actual_kg > 0 else slot.weighted_cost_per_kg
    slot.weighted_cost_per_kg = (
        (slot.quantity_kg * slot.weighted_cost_per_kg) + (actual_kg * new_cost)
    ) / new_total_qty
    slot.quantity_kg = new_total_qty


def dispatch_transfer(db: Session, transfer: Transfer) -> None:
    factory_slot = inventory_slot(db, LocationType.factory, FACTORY_LOCATION_ID, transfer.product_id)
    if factory_slot.quantity_kg < transfer.qty_kg:
        raise ValueError("Insufficient finished stock in factory")
    factory_slot.quantity_kg -= transfer.qty_kg


def receive_transfer(
    db: Session,
    transfer: Transfer,
    received_qty_kg: float | None = None,
    requested_by_user_id: int | None = None,
) -> None:
    if transfer.status == TransferStatus.received:
        raise ValueError("Transfer already received")
    if received_qty_kg is None:
        received_qty_kg = transfer.qty_kg
    if received_qty_kg <= 0:
        raise ValueError("Received quantity must be positive")
    if requested_by_user_id is None:
        raise ValueError("requested_by_user_id is required")

    factory_slot = inventory_slot(db, LocationType.factory, FACTORY_LOCATION_ID, transfer.product_id)
    store_slot = inventory_slot(db, LocationType.store, transfer.to_store_id, transfer.product_id)

    # Snapshot factory cost at time of receiving (before crediting back any difference)
    cost_per_kg = factory_slot.weighted_cost_per_kg
    store_slot.weighted_cost_per_kg = cost_per_kg
    store_slot.quantity_kg += received_qty_kg

    difference = transfer.qty_kg - received_qty_kg
    if abs(difference) > 0:
        # Credit any shortfall back to factory (fixes stock-leak on under-receive)
        if difference > 0:
            factory_slot.quantity_kg += difference

        status = (
            ApprovalStatus.pending
            if abs(difference) > settings.transfer_diff_auto_approve_kg
            else ApprovalStatus.approved
        )
        db.add(
            TransferException(
                transfer_id=transfer.id,
                expected_qty_kg=transfer.qty_kg,
                received_qty_kg=received_qty_kg,
                difference_qty_kg=difference,
                status=status,
                requested_by_user_id=requested_by_user_id,
            )
        )
    transfer.status = TransferStatus.received


def apply_store_movement(db: Session, movement: StoreMovement) -> None:
    slot = inventory_slot(db, LocationType.store, movement.store_id, movement.product_id)
    if movement.movement_type in (MovementType.sale, MovementType.waste):
        if slot.quantity_kg < movement.qty_kg:
            raise ValueError("Insufficient store stock")
        slot.quantity_kg -= movement.qty_kg
    elif movement.movement_type == MovementType.return_:
        slot.quantity_kg += movement.qty_kg


def create_inventory_adjustment(
    db: Session,
    location_type: LocationType,
    location_id: int,
    product_id: int,
    qty_delta_kg: float,
    reason: str,
    requested_by_user_id: int,
) -> InventoryAdjustment:
    status = (
        ApprovalStatus.pending
        if abs(qty_delta_kg) > settings.stock_adjustment_auto_approve_kg
        else ApprovalStatus.approved
    )
    adj = InventoryAdjustment(
        location_type=location_type,
        location_id=location_id,
        product_id=product_id,
        qty_delta_kg=qty_delta_kg,
        reason=reason,
        status=status,
        requested_by_user_id=requested_by_user_id,
        approved_by_user_id=requested_by_user_id if status == ApprovalStatus.approved else None,
    )
    db.add(adj)
    db.flush()
    if status == ApprovalStatus.approved:
        slot = inventory_slot(db, location_type, location_id, product_id)
        if qty_delta_kg < 0 and slot.quantity_kg < abs(qty_delta_kg):
            raise ValueError("Insufficient stock for negative adjustment")
        slot.quantity_kg += qty_delta_kg
    return adj


def approve_inventory_adjustment(
    db: Session, adjustment: InventoryAdjustment, approved_by_user_id: int
) -> InventoryAdjustment:
    if adjustment.status != ApprovalStatus.pending:
        raise ValueError("Adjustment is not pending")
    slot = inventory_slot(
        db, adjustment.location_type, adjustment.location_id, adjustment.product_id
    )
    if adjustment.qty_delta_kg < 0 and slot.quantity_kg < abs(adjustment.qty_delta_kg):
        raise ValueError("Insufficient stock for negative adjustment")
    slot.quantity_kg += adjustment.qty_delta_kg
    adjustment.status = ApprovalStatus.approved
    adjustment.approved_by_user_id = approved_by_user_id
    return adjustment


def reject_inventory_adjustment(
    db: Session, adjustment: InventoryAdjustment, approved_by_user_id: int
) -> InventoryAdjustment:
    if adjustment.status != ApprovalStatus.pending:
        raise ValueError("Adjustment is not pending")
    adjustment.status = ApprovalStatus.rejected
    adjustment.approved_by_user_id = approved_by_user_id
    return adjustment


def approve_transfer_exception(
    db: Session, transfer_exception: TransferException, approved_by_user_id: int
) -> TransferException:
    if transfer_exception.status != ApprovalStatus.pending:
        raise ValueError("Transfer exception is not pending")
    transfer_exception.status = ApprovalStatus.approved
    transfer_exception.approved_by_user_id = approved_by_user_id
    return transfer_exception


def reject_transfer_exception(
    db: Session, transfer_exception: TransferException, approved_by_user_id: int
) -> TransferException:
    if transfer_exception.status != ApprovalStatus.pending:
        raise ValueError("Transfer exception is not pending")
    transfer_exception.status = ApprovalStatus.rejected
    transfer_exception.approved_by_user_id = approved_by_user_id
    return transfer_exception


def low_stock_items(db: Session) -> list[dict]:
    rows = db.execute(
        select(
            Product.id,
            Product.code,
            Product.name,
            Product.reorder_level,
            func.coalesce(Inventory.quantity_kg, 0.0),
        )
        .join(
            Inventory,
            (Inventory.product_id == Product.id)
            & (Inventory.location_type == LocationType.factory)
            & (Inventory.location_id == FACTORY_LOCATION_ID),
            isouter=True,
        )
        .where(Product.reorder_level > 0)
    ).all()
    return [
        {
            "product_id": product_id,
            "code": code,
            "name": name,
            "quantity_kg": round(float(qty), 3),
            "reorder_level": round(float(reorder_level), 3),
        }
        for product_id, code, name, reorder_level, qty in rows
        if float(qty) <= float(reorder_level)
    ]


def inventory_total_value(db: Session) -> float:
    total = db.scalar(
        select(func.coalesce(func.sum(Inventory.quantity_kg * Inventory.weighted_cost_per_kg), 0.0))
    )
    return round(float(total), 2)


def pending_approval_counts(db: Session) -> dict:
    adjustments = db.scalar(
        select(func.count(InventoryAdjustment.id)).where(
            InventoryAdjustment.status == ApprovalStatus.pending
        )
    )
    exceptions = db.scalar(
        select(func.count(TransferException.id)).where(
            TransferException.status == ApprovalStatus.pending
        )
    )
    return {
        "adjustments": int(adjustments or 0),
        "transfer_exceptions": int(exceptions or 0),
        "total": int((adjustments or 0) + (exceptions or 0)),
    }


def recent_activity(db: Session, limit: int = 12) -> list[dict]:
    """Return the latest ERP events merged and sorted by created_at."""
    product_names = {
        row.id: row.name
        for row in db.execute(select(Product.id, Product.name)).all()
    }

    events: list[dict] = []

    for r in db.scalars(select(Receiving).order_by(Receiving.id.desc()).limit(limit)).all():
        events.append(
            {
                "type": "receiving",
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "product": product_names.get(r.product_id, r.product_id),
                "qty_kg": round(r.qty_kg, 3),
                "detail": f"lot {r.lot_no}" if r.lot_no else "",
            }
        )
    for b in db.scalars(select(ProductionBatch).order_by(ProductionBatch.id.desc()).limit(limit)).all():
        events.append(
            {
                "type": "production",
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "product": product_names.get(b.finished_product_id, b.finished_product_id),
                "qty_kg": round(b.actual_kg, 3),
                "detail": f"waste {round(b.waste_kg, 3)} kg",
            }
        )
    for tr in db.scalars(select(Transfer).order_by(Transfer.id.desc()).limit(limit)).all():
        events.append(
            {
                "type": "transfer",
                "created_at": tr.created_at.isoformat() if tr.created_at else None,
                "product": product_names.get(tr.product_id, tr.product_id),
                "qty_kg": round(tr.qty_kg, 3),
                "detail": tr.status.value if hasattr(tr.status, "value") else str(tr.status),
            }
        )
    for m in db.scalars(select(StoreMovement).order_by(StoreMovement.id.desc()).limit(limit)).all():
        mtype = m.movement_type.value if hasattr(m.movement_type, "value") else str(m.movement_type)
        events.append(
            {
                "type": mtype.rstrip("_"),
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "product": product_names.get(m.product_id, m.product_id),
                "qty_kg": round(m.qty_kg, 3),
                "detail": "",
            }
        )

    events.sort(key=lambda e: e["created_at"] or "", reverse=True)
    return events[:limit]


def dashboard_summary(db: Session) -> dict:
    total_raw = db.scalar(
        select(func.coalesce(func.sum(Inventory.quantity_kg), 0.0))
        .join(Product, Product.id == Inventory.product_id)
        .where(Product.category == ProductCategory.raw)
    )
    total_finished = db.scalar(
        select(func.coalesce(func.sum(Inventory.quantity_kg), 0.0))
        .join(Product, Product.id == Inventory.product_id)
        .where(Product.category == ProductCategory.finished)
    )
    total_produced = db.scalar(
        select(func.coalesce(func.sum(ProductionBatch.actual_kg), 0.0))
    )
    total_waste = db.scalar(
        select(func.coalesce(func.sum(ProductionBatch.waste_kg), 0.0))
    )
    total_sales = db.scalar(
        select(func.coalesce(func.sum(StoreMovement.qty_kg), 0.0)).where(
            StoreMovement.movement_type == MovementType.sale
        )
    )
    low_stock = low_stock_items(db)
    approvals = pending_approval_counts(db)
    return {
        "raw_stock_kg": round(float(total_raw), 3),
        "finished_stock_kg": round(float(total_finished), 3),
        "produced_kg": round(float(total_produced), 3),
        "waste_kg": round(float(total_waste), 3),
        "sales_kg": round(float(total_sales), 3),
        "inventory_value": inventory_total_value(db),
        "low_stock_count": len(low_stock),
        "low_stock": low_stock,
        "pending_approvals": approvals,
        "recent_activity": recent_activity(db),
    }


def report_inventory_value(db: Session) -> list[dict]:
    rows = db.execute(
        select(
            Product.category,
            func.coalesce(func.sum(Inventory.quantity_kg), 0.0),
            func.coalesce(
                func.sum(Inventory.quantity_kg * Inventory.weighted_cost_per_kg), 0.0
            ),
        )
        .join(Product, Product.id == Inventory.product_id)
        .group_by(Product.category)
    ).all()
    return [
        {
            "category": category.value if hasattr(category, "value") else str(category),
            "total_qty_kg": round(float(qty), 3),
            "total_value": round(float(value), 2),
        }
        for category, qty, value in rows
    ]


def report_production_yield(db: Session, skip: int = 0, limit: int = 100) -> list[dict]:
    product_names = {
        row.id: row.name for row in db.execute(select(Product.id, Product.name)).all()
    }
    batches = db.scalars(
        select(ProductionBatch).order_by(ProductionBatch.id.desc()).offset(skip).limit(limit)
    ).all()
    return [
        {
            "batch_id": b.id,
            "product": product_names.get(b.finished_product_id, b.finished_product_id),
            "target_kg": round(b.target_kg, 3),
            "actual_kg": round(b.actual_kg, 3),
            "waste_kg": round(b.waste_kg, 3),
            "yield_pct": round((b.actual_kg / b.target_kg) * 100, 1) if b.target_kg else 0.0,
        }
        for b in batches
    ]
