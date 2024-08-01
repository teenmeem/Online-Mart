from sqlmodel import SQLModel, Field, Relationship
from sqlmodel import SQLModel, Field, create_engine, Relationship
from datetime import datetime


class InventoryTransaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
 #   inventory_id: int = Field(foreign_key="inventory.id")
    product_id: int
    transaction_type: str
    quantity: int
    unit_price: float
    transaction_date: datetime = Field(default_factory=datetime.now)
    source_destination: str | None  # Supplier/Customer
    remarks: str | None
    user_id: int
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={
        "onupdate": datetime.now})
#    inventory: "Inventory" = Relationship(back_populates="transactions")


# Model examples
example_input_inventory_trans = {
    "product_id": 1,
    "transaction_type": "IN",
    "quantity": 5,
    "unit_price": 100.00,
    "transaction_date": datetime.now(),
    "source_destination": "Supplier",
    "remarks": "Received from supplier",
    "user_id": 1
}


class InventoryTransCreate(SQLModel):
    product_id: int
    transaction_type: str
    quantity: int
    unit_price: float
    transaction_date: datetime = Field(default_factory=datetime.now)
    source_destination: str | None  # Supplier/Customer
    remarks: str | None
    user_id: int

    class Config:
        json_schema_extra = {"example": example_input_inventory_trans}


class InventoryTransUpdate(SQLModel):
    transaction_type: str | None
    quantity: int | None
    unit_price: float | None
    transaction_date: datetime | None
    source_destination: str | None
    remarks: str | None
    user_id: int | None


class InventoryTransResponse(SQLModel):
    id: int
    transaction_type: str | None
    quantity: int | None
    unit_price: float | None
    transaction_date: datetime | None
    source_destination: str | None
    remarks: str | None
    user_id: int | None


class InventoryTransDelete(SQLModel):
    id: int
    transaction_type: str
