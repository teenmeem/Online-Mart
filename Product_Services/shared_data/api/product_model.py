from sqlmodel import SQLModel, Field
from datetime import datetime


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True)
    description: str | None = None
    price: float
    stock: int
    location: str
    user_id: int
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={
        "onupdate": datetime.now}
    )


class ProductCreate(SQLModel):
    name: str
    description: str | None = None
    price: float
    stock: int
    location: str
    user_id: int


class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    location: str | None = None
    user_id: int | None = None


class ProductResponse(SQLModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    location: str
    user_id: int
