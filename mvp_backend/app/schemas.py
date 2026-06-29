from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import ApprovalStatus, LocationType, MovementType, ProductCategory, TransferStatus, UserRole

# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class SupplierCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class StoreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class ProductCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=120)
    category: ProductCategory
    unit: str = "kg"
    reorder_level: float = Field(ge=0, default=0.0)


class RecipeItemInput(BaseModel):
    ingredient_product_id: int
    qty_per_kg_output: float = Field(gt=0)


class RecipeCreate(BaseModel):
    finished_product_id: int
    items: list[RecipeItemInput] = Field(min_length=1)


class ReceivingCreate(BaseModel):
    supplier_id: int
    product_id: int
    qty_kg: float = Field(gt=0)
    unit_cost: float = Field(gt=0)
    lot_no: str = Field(default="", max_length=60)


class ProductionComplete(BaseModel):
    finished_product_id: int
    target_kg: float = Field(gt=0)
    actual_kg: float = Field(gt=0)
    waste_kg: float = Field(ge=0, default=0)


class TransferDispatch(BaseModel):
    product_id: int
    qty_kg: float = Field(gt=0)
    to_store_id: int


class TransferReceive(BaseModel):
    received_qty_kg: float = Field(gt=0)


class StoreMovementCreate(BaseModel):
    product_id: int
    movement_type: MovementType
    qty_kg: float = Field(gt=0)
    unit_price: float = Field(ge=0, default=0.0)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=64)
    role: UserRole


class InventoryAdjustmentCreate(BaseModel):
    location_type: LocationType
    location_id: int = 0
    product_id: int
    qty_delta_kg: float
    reason: str = Field(min_length=3, max_length=240)

    @field_validator("qty_delta_kg")
    @classmethod
    def qty_delta_not_zero(cls, v: float) -> float:
        if v == 0:
            raise ValueError("qty_delta_kg must not be zero")
        return v


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------

_ORM = ConfigDict(from_attributes=True)


class SupplierOut(BaseModel):
    model_config = _ORM
    id: int
    name: str


class StoreOut(BaseModel):
    model_config = _ORM
    id: int
    name: str


class ProductOut(BaseModel):
    model_config = _ORM
    id: int
    code: str
    name: str
    category: ProductCategory
    unit: str
    reorder_level: float


class RecipeItemOut(BaseModel):
    ingredient_product_id: int
    ingredient_name: str | None
    ingredient_code: str | None
    qty_per_kg_output: float


class RecipeOut(BaseModel):
    id: int
    finished_product_id: int
    finished_code: str | None
    finished_name: str | None
    items: list[RecipeItemOut]


class ReceivingOut(BaseModel):
    id: int
    supplier_id: int
    supplier_name: str | None
    product_id: int
    product_name: str | None
    qty_kg: float
    unit_cost: float
    lot_no: str
    created_at: str | None


class ProductionBatchOut(BaseModel):
    id: int
    finished_product_id: int
    finished_name: str | None
    target_kg: float
    actual_kg: float
    waste_kg: float
    created_at: str | None


class TransferOut(BaseModel):
    model_config = _ORM
    id: int
    product_id: int
    product_name: str | None = None
    qty_kg: float
    to_store_id: int
    to_store_name: str | None = None
    status: TransferStatus
    created_at: str | None = None


class StoreMovementOut(BaseModel):
    id: int
    store_id: int
    store_name: str | None
    product_id: int
    product_name: str | None
    movement_type: MovementType
    qty_kg: float
    unit_price: float
    created_at: str | None


class InventoryOut(BaseModel):
    location_type: LocationType
    location_id: int
    location_name: str
    product_id: int
    product_code: str | None
    product_name: str | None
    quantity_kg: float
    weighted_cost_per_kg: float
    value: float


class InventoryAdjustmentOut(BaseModel):
    id: int
    location_type: LocationType
    location_id: int
    product_id: int
    product_name: str | None
    qty_delta_kg: float
    reason: str
    status: ApprovalStatus
    created_at: str | None


class TransferExceptionOut(BaseModel):
    id: int
    transfer_id: int
    expected_qty_kg: float
    received_qty_kg: float
    difference_qty_kg: float
    status: ApprovalStatus
    created_at: str | None


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole
    is_active: bool


# --- action responses ---

class AdjustmentActionOut(BaseModel):
    adjustment_id: int
    status: ApprovalStatus


class ExceptionActionOut(BaseModel):
    exception_id: int
    status: ApprovalStatus


class BatchCreateOut(BaseModel):
    batch_id: int
    consumed: list[dict]


class ImportResultOut(BaseModel):
    imported_rows: int


# --- dashboard / reports ---

class LowStockItemOut(BaseModel):
    product_id: int
    code: str
    name: str
    quantity_kg: float
    reorder_level: float


class PendingApprovalsOut(BaseModel):
    adjustments: int
    transfer_exceptions: int
    total: int


class RecentActivityOut(BaseModel):
    type: str
    created_at: str | None
    product: str | int
    qty_kg: float
    detail: str


class DashboardSummaryOut(BaseModel):
    raw_stock_kg: float
    finished_stock_kg: float
    produced_kg: float
    waste_kg: float
    sales_kg: float
    inventory_value: float
    low_stock_count: int
    low_stock: list[LowStockItemOut]
    pending_approvals: PendingApprovalsOut
    recent_activity: list[RecentActivityOut]
