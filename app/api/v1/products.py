"""HTTP endpoints for product catalog queries."""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.product import Product, ProductPage
from app.services.product_service import (
    InvalidProductFilterError,
    ProductNotFoundError,
    ProductService,
)
from app.repositories.product_repository import ProductRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["Products"])
product_service = ProductService(ProductRepository())


@router.get("", response_model=ProductPage)
async def list_products(limit: int = 20, offset: int = 0) -> ProductPage:
    try:
        result = product_service.list_products(limit=limit, offset=offset)
    except InvalidProductFilterError as exc:
        logger.warning("Invalid product pagination: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProductPage.model_validate(result)


@router.get("/search", response_model=ProductPage)
async def search_products(
    brand: str | None = None,
    category: str | None = None,
    ram_gb: int | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> ProductPage:
    filters = {
        "brand": brand,
        "category": category,
        "ram_gb": ram_gb,
        "min_price": min_price,
        "max_price": max_price,
    }
    logger.info("Incoming product search: %s", filters)
    try:
        result = product_service.search_products(
            **filters,
            limit=limit,
            offset=offset,
        )
    except InvalidProductFilterError as exc:
        logger.warning("Invalid product search filters %s: %s", filters, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProductPage.model_validate(result)


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str) -> Product:
    logger.info("Product lookup: id=%s", product_id)
    try:
        result = product_service.get_product(product_id)
    except ProductNotFoundError as exc:
        logger.warning("Product not found: id=%s", product_id)
        raise HTTPException(status_code=404, detail="Product not found") from exc
    return Product.model_validate(result)
