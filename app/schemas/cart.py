"""Pydantic models for shopping cart tool results."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CartAddRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    product_id: str = Field(min_length=1)
    quantity: int = Field(default=1, gt=0)


class CartRemoveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    product_id: str = Field(min_length=1)


class CartItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cart_id: int = Field(gt=0)
    product_id: str
    quantity: int = Field(gt=0)
    added_at: datetime
    brand: str
    model_name: str
    price: int = Field(ge=0)
    line_total: int = Field(ge=0)


class CartResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_items: int = Field(ge=0)
    total_price: int = Field(ge=0)
    items: list[CartItem]
