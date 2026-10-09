import pytest

from app.services.cart_service import (
    InsufficientStockError,
    ProductOutOfStockError,
)


def test_add_available_product_and_calculate_cart_total(clean_cart):
    cart = clean_cart.add_product("LAP-001", quantity=2)
    assert cart.total_items == 2
    assert cart.total_price == 79980
    assert cart.items[0].quantity == 2


def test_reject_out_of_stock_and_excess_quantity(clean_cart):
    with pytest.raises(ProductOutOfStockError):
        clean_cart.add_product("LAP-003")
    with pytest.raises(InsufficientStockError):
        clean_cart.add_product("LAP-001", quantity=9)
    assert clean_cart.get_cart().total_items == 0


def test_remove_product_and_clear_cart(clean_cart):
    clean_cart.add_product("LAP-001", quantity=1)
    clean_cart.add_product("LAP-002", quantity=1)
    after_remove = clean_cart.remove_product("LAP-001")
    assert [item.product_id for item in after_remove.items] == ["LAP-002"]

    after_clear = clean_cart.clear_cart()
    assert after_clear.items == []
    assert after_clear.total_items == 0
    assert after_clear.total_price == 0
