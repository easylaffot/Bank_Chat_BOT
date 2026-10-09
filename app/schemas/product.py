"""Pydantic response models for the product catalog API."""

from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    brand: str
    model_name: str
    category: str
    price: int = Field(ge=0)
    ram_gb: int = Field(gt=0)
    processor: str
    storage_gb: int = Field(gt=0)
    battery_hours: float = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    delivery_days: int = Field(ge=0)
    rating: float = Field(ge=0, le=5)


class ProductPage(BaseModel):
    total: int = Field(ge=0)
    count: int = Field(ge=0)
    items: list[Product]
