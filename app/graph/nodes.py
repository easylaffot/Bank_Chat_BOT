"""LangGraph nodes; each node delegates to exactly one agent."""

import logging
from typing import Any

from app.agents.budget_agent import BudgetAgent
from app.agents.comparison_agent import ComparisonAgent
from app.agents.inventory_agent import InventoryAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.search_agent import (
    InvalidCustomerQueryError,
    NoProductsFoundError,
    SearchAgent,
)
from app.graph.state import ShoppingState

logger = logging.getLogger(__name__)
_default_search_agent = SearchAgent()
_default_comparison_agent = ComparisonAgent()
_default_inventory_agent = InventoryAgent()
_default_budget_agent = BudgetAgent()
_default_recommendation_agent = RecommendationAgent()


def search_node(
    state: ShoppingState,
    *,
    agent: SearchAgent | None = None,
) -> dict[str, Any]:
    logger.info("Graph transition: search agent")
    try:
        results = (agent or _default_search_agent).run(state.get("user_query", ""))
    except InvalidCustomerQueryError as exc:
        logger.warning("Search agent rejected customer query: %s", exc)
        return {
            "search_results": {"intent": {}, "matches": []},
            "error": {"code": "invalid_query", "message": str(exc)},
        }
    except NoProductsFoundError as exc:
        logger.info("Search agent found no products: %s", exc)
        code = "budget_too_low" if exc.intent.budget is not None else "no_products_found"
        return {
            "search_results": {"intent": exc.intent.model_dump(), "matches": []},
            "error": {"code": code, "message": str(exc)},
        }
    except Exception:
        logger.exception("Search agent failed")
        return {
            "search_results": {"intent": {}, "matches": []},
            "error": {
                "code": "search_error",
                "message": "The product search could not be completed.",
            },
        }

    logger.info("Graph transition: search completed with %d matches", len(results["matches"]))
    return {"search_results": results, "error": None}


def comparison_node(
    state: ShoppingState,
    *,
    agent: ComparisonAgent | None = None,
) -> dict[str, Any]:
    logger.info("Graph transition: comparison agent")
    try:
        results = (agent or _default_comparison_agent).run(
            state.get("search_results", {}).get("matches", [])
        )
        return {"comparison_results": results}
    except Exception:
        logger.exception("Comparison agent failed")
        return {
            "comparison_results": [],
            "error": {"code": "comparison_error", "message": "Product comparison failed."},
        }


def inventory_node(
    state: ShoppingState,
    *,
    agent: InventoryAgent | None = None,
) -> dict[str, Any]:
    logger.info("Graph transition: inventory agent")
    try:
        results = (agent or _default_inventory_agent).run(
            state.get("search_results", {}).get("matches", [])
        )
        return {"inventory_results": results}
    except Exception:
        logger.exception("Inventory agent failed")
        return {
            "inventory_results": {},
            "error": {"code": "inventory_error", "message": "Product availability could not be checked."},
        }


def budget_node(
    state: ShoppingState,
    *,
    agent: BudgetAgent | None = None,
) -> dict[str, Any]:
    logger.info("Graph transition: budget agent")
    try:
        results = (agent or _default_budget_agent).run(
            state.get("search_results", {}).get("matches", []),
            state.get("search_results", {}).get("intent", {}),
        )
        return {"budget_results": results}
    except Exception:
        logger.exception("Budget agent failed")
        return {
            "budget_results": {"budget": None, "results": {}},
            "error": {"code": "budget_error", "message": "Product affordability could not be checked."},
        }


def recommendation_node(
    state: ShoppingState,
    *,
    agent: RecommendationAgent | None = None,
) -> dict[str, Any]:
    logger.info("Graph transition: recommendation agent")
    try:
        recommendation = (agent or _default_recommendation_agent).run(state)
        return {"recommendation": recommendation}
    except Exception:
        logger.exception("Recommendation agent failed")
        return {
            "recommendation": {
                "recommended_product": None,
                "reason": "A recommendation could not be generated.",
                "alternatives": [],
            }
        }
