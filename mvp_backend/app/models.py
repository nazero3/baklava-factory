from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ProductCategory(str, Enum):
    raw = "raw"
    finished = "finished"


class LocationType(str, Enum):
    factory = "factory"
    store = "store"


class TransferStatus(str, Enum):
    dispatched = "dispatched"
    received = "received"


class MovementType(str, Enum):
    sale = "sale"
    return_ = "return"
    waste = "waste"


class UserRole(str, Enum):
    admin = "admin"
    executive = "executive"
    factory_manager = "factory_manager"
    warehouse = "warehouse"
    production_supervisor = "production_supervisor"
    store_manager = "store_manager"
    accountant = "accountant"


class ApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[ProductCategory] = mapped_column(SAEnum(ProductCategory))
    unit: Mapped[str] = mapped_column(String(10), default="kg")


class Recipe(Base):
    __tablename__ = "recipes"
    __table_args__ = (UniqueConstraint("finished_product_id", name="uq_recipe_finished"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    finished_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    items: Mapped[list["RecipeItem"]] = relationship(cascade="all, delete-orphan")


class RecipeItem(Base):
    __tablename__ = "recipe_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    ingredient_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty_per_kg_output: Mapped[float] = mapped_column(Float)


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("location_type", "location_id", "product_id", name="uq_inventory_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    location_type: Mapped[LocationType] = mapped_column(SAEnum(LocationType))
    location_id: Mapped[int] = mapped_column(default=0)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity_kg: Mapped[float] = mapped_column(Float, default=0.0)
    weighted_cost_per_kg: Mapped[float] = mapped_column(Float, default=0.0)


class Receiving(Base):
    __tablename__ = "receivings"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty_kg: Mapped[float] = mapped_column(Float)
    unit_cost: Mapped[float] = mapped_column(Float)
    lot_no: Mapped[str] = mapped_column(String(60), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ProductionBatch(Base):
    __tablename__ = "production_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    finished_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    target_kg: Mapped[float] = mapped_column(Float)
    actual_kg: Mapped[float] = mapped_column(Float)
    waste_kg: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty_kg: Mapped[float] = mapped_column(Float)
    to_store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"))
    status: Mapped[TransferStatus] = mapped_column(SAEnum(TransferStatus), default=TransferStatus.dispatched)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class StoreMovement(Base):
    __tablename__ = "store_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    movement_type: Mapped[MovementType] = mapped_column(SAEnum(MovementType))
    qty_kg: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(128))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole))
    api_token: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_type: Mapped[LocationType] = mapped_column(SAEnum(LocationType))
    location_id: Mapped[int] = mapped_column(default=0)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty_delta_kg: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(String(240))
    status: Mapped[ApprovalStatus] = mapped_column(SAEnum(ApprovalStatus), default=ApprovalStatus.pending)
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class TransferException(Base):
    __tablename__ = "transfer_exceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    transfer_id: Mapped[int] = mapped_column(ForeignKey("transfers.id"))
    expected_qty_kg: Mapped[float] = mapped_column(Float)
    received_qty_kg: Mapped[float] = mapped_column(Float)
    difference_qty_kg: Mapped[float] = mapped_column(Float)
    status: Mapped[ApprovalStatus] = mapped_column(SAEnum(ApprovalStatus), default=ApprovalStatus.pending)
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
