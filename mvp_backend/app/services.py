from sqlalchemy import func, select
from sqlalchemy.orm import Session

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
    RecipeItem,
    Receiving,
    StoreMovement,
    Transfer,
    TransferException,
    TransferStatus,
)

STOCK_ADJUSTMENT_AUTO_APPROVE_KG = 1.0
TRANSFER_DIFF_AUTO_APPROVE_KG = 0.2


def inventory_slot(db: Session, location_type: LocationType, location_id: int, product_id: int) -> Inventory:
    slot = db.scalar(
        select(Inventory).where(
            Inventory.location_type == location_type,
            Inventory.location_id == location_id,
            Inventory.product_id == product_id,
        )
    )
    if not slot:
        slot = Inventory(location_type=location_type, location_id=location_id, product_id=product_id, quantity_kg=0, weighted_cost_per_kg=0)
        db.add(slot)
        db.flush()
    return slot


def apply_receiving(db: Session, receiving: Receiving) -> None:
    slot = inventory_slot(db, LocationType.factory, 0, receiving.product_id)
    new_total_qty = slot.quantity_kg + receiving.qty_kg
    if new_total_qty <= 0:
        return
    slot.weighted_cost_per_kg = ((slot.quantity_kg * slot.weighted_cost_per_kg) + (receiving.qty_kg * receiving.unit_cost)) / new_total_qty
    slot.quantity_kg = new_total_qty


def consume_for_production(db: Session, finished_product_id: int, actual_kg: float) -> tuple[float, list[dict]]:
    recipe = db.scalar(select(Recipe).where(Recipe.finished_product_id == finished_product_id))
    if not recipe:
        raise ValueError("No recipe found for finished product")

    consumed_cost = 0.0
    consumed_rows = []
    items = db.scalars(select(RecipeItem).where(RecipeItem.recipe_id == recipe.id)).all()
    for item in items:
        qty_needed = item.qty_per_kg_output * actual_kg
        raw_slot = inventory_slot(db, LocationType.factory, 0, item.ingredient_product_id)
        if raw_slot.quantity_kg < qty_needed:
            raise ValueError("Insufficient raw material for production")
        raw_slot.quantity_kg -= qty_needed
        consumed_cost += qty_needed * raw_slot.weighted_cost_per_kg
        consumed_rows.append({"ingredient_product_id": item.ingredient_product_id, "qty_kg": qty_needed})
    return consumed_cost, consumed_rows


def post_finished_goods(db: Session, finished_product_id: int, actual_kg: float, total_cost: float) -> None:
    slot = inventory_slot(db, LocationType.factory, 0, finished_product_id)
    new_total_qty = slot.quantity_kg + actual_kg
    if new_total_qty <= 0:
        return
    new_cost = total_cost / actual_kg if actual_kg > 0 else slot.weighted_cost_per_kg
    slot.weighted_cost_per_kg = ((slot.quantity_kg * slot.weighted_cost_per_kg) + (actual_kg * new_cost)) / new_total_qty
    slot.quantity_kg = new_total_qty


def dispatch_transfer(db: Session, transfer: Transfer) -> None:
    factory_slot = inventory_slot(db, LocationType.factory, 0, transfer.product_id)
    if factory_slot.quantity_kg < transfer.qty_kg:
        raise ValueError("Insufficient finished stock in factory")
    factory_slot.quantity_kg -= transfer.qty_kg


def receive_transfer(db: Session, transfer: Transfer, received_qty_kg: float | None = None, requested_by_user_id: int | None = None) -> None:
    if transfer.status == TransferStatus.received:
        raise ValueError("Transfer already received")
    if received_qty_kg is None:
        received_qty_kg = transfer.qty_kg
    if received_qty_kg <= 0:
        raise ValueError("Received quantity must be positive")
    factory_slot = inventory_slot(db, LocationType.factory, 0, transfer.product_id)
    store_slot = inventory_slot(db, LocationType.store, transfer.to_store_id, transfer.product_id)
    store_slot.weighted_cost_per_kg = factory_slot.weighted_cost_per_kg
    store_slot.quantity_kg += received_qty_kg

    difference = transfer.qty_kg - received_qty_kg
    if abs(difference) > 0:
        status = ApprovalStatus.pending if abs(difference) > TRANSFER_DIFF_AUTO_APPROVE_KG else ApprovalStatus.approved
        db.add(
            TransferException(
                transfer_id=transfer.id,
                expected_qty_kg=transfer.qty_kg,
                received_qty_kg=received_qty_kg,
                difference_qty_kg=difference,
                status=status,
                requested_by_user_id=requested_by_user_id or 1,
            )
        )
    transfer.status = TransferStatus.received


def apply_store_movement(db: Session, movement: StoreMovement) -> None:
    slot = inventory_slot(db, LocationType.store, movement.store_id, movement.product_id)
    if movement.movement_type == MovementType.sale or movement.movement_type == MovementType.waste:
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
    status = ApprovalStatus.pending if abs(qty_delta_kg) > STOCK_ADJUSTMENT_AUTO_APPROVE_KG else ApprovalStatus.approved
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


def approve_inventory_adjustment(db: Session, adjustment: InventoryAdjustment, approved_by_user_id: int) -> InventoryAdjustment:
    if adjustment.status != ApprovalStatus.pending:
        raise ValueError("Adjustment is not pending")
    slot = inventory_slot(db, adjustment.location_type, adjustment.location_id, adjustment.product_id)
    if adjustment.qty_delta_kg < 0 and slot.quantity_kg < abs(adjustment.qty_delta_kg):
        raise ValueError("Insufficient stock for negative adjustment")
    slot.quantity_kg += adjustment.qty_delta_kg
    adjustment.status = ApprovalStatus.approved
    adjustment.approved_by_user_id = approved_by_user_id
    return adjustment


def approve_transfer_exception(db: Session, transfer_exception: TransferException, approved_by_user_id: int) -> TransferException:
    if transfer_exception.status != ApprovalStatus.pending:
        raise ValueError("Transfer exception is not pending")
    transfer_exception.status = ApprovalStatus.approved
    transfer_exception.approved_by_user_id = approved_by_user_id
    return transfer_exception


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
    total_produced = db.scalar(select(func.coalesce(func.sum(ProductionBatch.actual_kg), 0.0)))
    total_waste = db.scalar(select(func.coalesce(func.sum(ProductionBatch.waste_kg), 0.0)))
    total_sales = db.scalar(
        select(func.coalesce(func.sum(StoreMovement.qty_kg), 0.0)).where(StoreMovement.movement_type == MovementType.sale)
    )
    return {
        "raw_stock_kg": round(float(total_raw), 3),
        "finished_stock_kg": round(float(total_finished), 3),
        "produced_kg": round(float(total_produced), 3),
        "waste_kg": round(float(total_waste), 3),
        "sales_kg": round(float(total_sales), 3),
    }
