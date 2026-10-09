from app.agents.search_agent import (
    InvalidCustomerQueryError,
    NoProductsFoundError,
    SearchIntent,
    SearchAgent,
)
from app.graph.shopping_graph import build_shopping_graph


class FakeSearchAgent:
    def __init__(self, products):
        self.products = products

    def run(self, query):
        return {
            "intent": {"budget": 60000, "category": "Programming", "ram_gb": 16},
            "matches": self.products,
        }


class FakeComparisonAgent:
    def run(self, products):
        return [
            {"product_id": product["id"], "score": 90 - index, "rank": index + 1}
            for index, product in enumerate(products)
        ]


class FakeInventoryAgent:
    def run(self, products):
        return {
            product["id"]: {"in_stock": True, "stock_quantity": 2, "delivery_days": 3}
            for product in products
        }


class FakeBudgetAgent:
    def run(self, products, intent):
        return {
            "budget": intent["budget"],
            "results": {
                product["id"]: {"within_budget": True, "remaining_budget": 3010}
                for product in products
            },
        }


class FakeRecommendationAgent:
    def run(self, state):
        products = state["search_results"]["matches"]
        return {
            "recommended_product": products[0],
            "reason": "Highest-ranked available product.",
            "alternatives": products[1:],
        }


class RaisingSearchAgent:
    def __init__(self, error):
        self.error = error

    def run(self, query):
        raise self.error


def test_valid_query_completes_graph_with_recommendation(sample_products):
    graph = build_shopping_graph(
        search_agent=FakeSearchAgent(sample_products[:2]),
        comparison_agent=FakeComparisonAgent(),
        inventory_agent=FakeInventoryAgent(),
        budget_agent=FakeBudgetAgent(),
        recommendation_agent=FakeRecommendationAgent(),
    )
    result = graph.invoke({"user_query": "programming laptop under 60000"})
    assert result["recommendation"]["recommended_product"]["id"] == "LAP-001"
    assert result["comparison_results"][0]["rank"] == 1
    assert result["budget_results"]["results"]["LAP-001"]["within_budget"] is True


def test_graph_returns_budget_and_invalid_query_errors():
    low_budget_graph = build_shopping_graph(
        search_agent=RaisingSearchAgent(
            NoProductsFoundError(
                "No products matched within budget",
                SearchIntent(budget=1),
            )
        )
    )
    low_budget = low_budget_graph.invoke({"user_query": "cheap laptop"})
    assert low_budget["error"]["code"] == "budget_too_low"

    invalid_graph = build_shopping_graph(search_agent=SearchAgent())
    invalid = invalid_graph.invoke({"user_query": "   "})
    assert invalid["error"]["code"] == "invalid_query"
