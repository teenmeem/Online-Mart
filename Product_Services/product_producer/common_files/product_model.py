from sqlmodel import SQLModel, Field
from datetime import datetime


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    prod_code: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    description: str | None = None
    category: str = Field(index=True)
    brand: str
    price: float
    currency: str
    stock: int
    location: str
#    sku: str | None = Field(unique=True, max_length=255)
    user_id: int = Field(index=True)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={
        "onupdate": datetime.now}
    )


# Model examples
example_input_product = {
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


class ProductCreate(SQLModel):
    prod_code: str
    name: str
    description: str | None = None
    category: str
    brand: str
    price: float
    currency: str
    stock: int
    location: str
    user_id: int

    class Config:
        json_schema_extra = {"example": example_input_product}


class ProductUpdate(SQLModel):
    prod_code: str | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None
    brand: str | None = None
    price: float | None = None
    currency: str | None = None
    stock: int | None = None
    location: str | None = None
    user_id: int | None = None


class ProductResponse(SQLModel):
    id: int
    prod_code: str | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None
    brand: str | None = None
    price: float | None = None
    currency: str | None = None
    stock: int | None = None
    location: str | None = None
    user_id: int | None = None
