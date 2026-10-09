from app.tools.budget_tool import check_budget
from app.tools.comparison_tool import compare_products
from app.tools.inventory_tool import check_inventory
from app.tools.search_tool import search_products


def test_product_search_respects_budget(temp_database):
    result = search_products(budget=60000)
    assert result["matches"]
    assert all(product["price"] <= 60000 for product in result["matches"])
    assert {product["id"] for product in result["matches"]} == {"LAP-001", "LAP-002"}


def test_inventory_reports_in_stock_and_out_of_stock_products(temp_database):
    available = check_inventory("LAP-001")
    unavailable = check_inventory("LAP-003")
    assert available == {"in_stock": True, "stock_quantity": 8, "delivery_days": 2}
    assert unavailable == {"in_stock": False}


def test_budget_reports_remaining_amount(temp_database):
    result = check_budget("LAP-002", 60000)
    assert result["within_budget"] is True
    assert result["remaining_budget"] == 3010


def test_comparison_ranks_best_product_first(temp_database):
    results = compare_products(["LAP-001", "LAP-002"])
    assert results[0]["product_id"] == "LAP-002"
    assert results[0]["rank"] == 1
    assert results[0]["score"] >= results[1]["score"]
