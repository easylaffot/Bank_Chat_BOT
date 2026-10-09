"""HTTP endpoints for the shopping cart."""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.cart import CartAddRequest, CartRemoveRequest, CartResponse
from app.services.cart_service import (
    CartItemNotFoundError,
    CartService,
    InsufficientStockError,
    InvalidCartQuantityError,
    ProductOutOfStockError,
)
from app.services.product_service import ProductNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cart", tags=["Cart"])
_cart_service = CartService()


@router.get("", response_model=CartResponse)
def read_cart() -> CartResponse:
    logger.info("Cart endpoint called: get")
    return _cart_service.get_cart()


@router.post("/add", response_model=CartResponse)
def add_cart_item(request: CartAddRequest) -> CartResponse:
    logger.info("Cart endpoint called: add product_id=%s", request.product_id)
    try:
        return _cart_service.add_product(request.product_id, request.quantity)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Product not found") from exc
    except (ProductOutOfStockError, InvalidCartQuantityError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except InsufficientStockError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/remove", response_model=CartResponse)
def remove_cart_item(request: CartRemoveRequest) -> CartResponse:
    logger.info("Cart endpoint called: remove product_id=%s", request.product_id)
    try:
        return _cart_service.remove_product(request.product_id)
    except CartItemNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Product is not in the cart") from exc


@router.delete("/clear", response_model=CartResponse)
def clear_cart() -> CartResponse:
    logger.info("Cart endpoint called: clear")
    return _cart_service.clear_cart()
