from pydantic import BaseModel, Field

from .models import LocationType, MovementType, ProductCategory, UserRole


class SupplierCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class StoreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class ProductCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=120)
    category: ProductCategory
    unit: str = "kg"


class RecipeItemInput(BaseModel):
    ingredient_product_id: int
    qty_per_kg_output: float = Field(gt=0)


class RecipeCreate(BaseModel):
    finished_product_id: int
    items: list[RecipeItemInput]


class ReceivingCreate(BaseModel):
    supplier_id: int
    product_id: int
    qty_kg: float = Field(gt=0)
    unit_cost: float = Field(gt=0)
    lot_no: str = ""


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


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=6, max_length=64)
    role: UserRole


class InventoryAdjustmentCreate(BaseModel):
    location_type: LocationType
    location_id: int = 0
    product_id: int
    qty_delta_kg: float
    reason: str = Field(min_length=3, max_length=240)
