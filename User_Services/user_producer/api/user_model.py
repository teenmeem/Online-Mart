# from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from fastapi import Form
from typing import Annotated


class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, )
    email: str = Field(unique=True, index=True, )
    # Add type hint and constraints
    password: str = Field(
        min_length=8, regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', nullable=False)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={
        "onupdate": datetime.now}
    )


class Register_User (SQLModel):
    username: Annotated[str, Form()]
    email: Annotated[str, Form()]
    password: Annotated[str, Form()]


class Token (SQLModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData (SQLModel):
    username: str


class RefreshTokenData (SQLModel):
    email: str
