from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int   # Reference to User Service
    order_date: datetime = Field(default_factory=datetime.now)
    status: str = Field(max_length=50)
    # = Field(        sa_column_kwargs={"type_": "DECIMAL(10, 2)"})
    total_amount: int | None
    shipping_address: str
    billing_address: str
    payment_method: str = Field(max_length=50)
    transaction_type: str
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={
        "onupdate": datetime.now})
    order_items: list["OrderItem"] = Relationship(back_populates="order",
                                                  sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int  # Reference to Product Service
    quantity: int
    # = Field(        sa_column_kwargs={"type_": "DECIMAL(10, 2)"})
    unit_price: float
    # = Field(        sa_column_kwargs={"type_": "DECIMAL(10, 2)"})
    total_price: float

    order: "Order" = Relationship(back_populates="order_items")


# Model examples
example_input_order = {
    "customer_id": 1,
    "status": "Pending",
    "shipping_address": "123 Main St",
    "billing_address": "123 Main St",
    "payment_method": "Credit Card",
    "transaction_type": "OUT",
    "order_items": [
        {
            "product_id": 2,
            "quantity": 5,
            "unit_price": 100000,
        }
    ]
}

# Pydantic models for request validation


class OrderItemCreate(SQLModel):
    product_id: int
    quantity: int
    unit_price: float

class OrderCreate(SQLModel):
    customer_id: int
    status: str
    shipping_address: str
    billing_address: str
    payment_method: str
    transaction_type: str
    order_items: list[OrderItemCreate]

    class Config:
        json_schema_extra = {"example": example_input_order}


# class InventoryTransCreate(SQLModel):
#     product_id: int
#     transaction_type: str
#     quantity: int
#     unit_price: float
#     transaction_date: datetime = Field(default_factory=datetime.now)
#     source_destination: str | None  # Supplier/Customer
#     remarks: str | None
#     user_id: int

#     class Config:
#         json_schema_extra = {"example": example_input_inventory_trans}


# class InventoryTransUpdate(SQLModel):
#     transaction_type: str | None
#     quantity: int | None
#     unit_price: float | None
#     transaction_date: datetime | None
#     source_destination: str | None
#     remarks: str | None
#     user_id: int | None


# class InventoryTransResponse(SQLModel):
#     id: int
#     transaction_type: str | None
#     quantity: int | None
#     unit_price: float | None
#     transaction_date: datetime | None
#     source_destination: str | None
#     remarks: str | None
#     user_id: int | None


# class InventoryTransDelete(SQLModel):
#     id: int
#     transaction_type: str
