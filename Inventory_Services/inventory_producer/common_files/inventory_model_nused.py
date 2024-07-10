from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from datetime import datetime
# from common_files.inventory_trans_model import InventoryTransaction


class Inventory_not_used(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int
    warehouse_location: str | None
    quantity_available: int
    reorder_level: int
    is_active: bool = Field(default=True)
    user_id: int = Field(index=True)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={
        "onupdate": datetime.now})
    # transactions: list["InventoryTransaction"] = Relationship(
    #     back_populates="inventory")
#    __table_args__ = (UniqueConstraint("product_id", "warehouse_location"))


# Model examples
example_input_inventory = {
    "prod_code": "ABC123",
    "name": "Car",
    "description": "Honda Accord",
    "category": "Vehicle",
    "brand": 'Honda',
    "price": 100000.00,
    "currency": "PKR",
    "stock": 5,
    "location": "Islmabad",
    "user_id": 1
}


class InventoryCreate(SQLModel):
    product_id: int
#    warehouse_location: str | None
#    quantity_available: int
    reorder_level: int
    is_active: bool
    user_id: int

    # class Config:
    #     json_schema_extra = {"example": example_input_inventory}


class InventoryUpdate(SQLModel):
    product_id: int | None
    warehouse_location: str | None
    quantity_available: int | None
    reorder_level: int | None
    is_active: bool | None
    user_id: int | None


class InventoryResponse(SQLModel):
    id: int
    product_id: int | None
    warehouse_location: str | None
    quantity_available: int | None
    reorder_level: int | None
    is_active: bool | None
    user_id: int | None
