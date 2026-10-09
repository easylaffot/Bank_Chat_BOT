"""Compile and run the LangGraph shopping workflow."""

import logging
from functools import partial

from langgraph.graph import END, START, StateGraph

from app.agents.budget_agent import BudgetAgent
from app.agents.comparison_agent import ComparisonAgent
from app.agents.inventory_agent import InventoryAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.search_agent import SearchAgent
from app.graph.nodes import (
    budget_node,
    comparison_node,
    inventory_node,
    recommendation_node,
    search_node,
)
from app.graph.state import ShoppingState

logger = logging.getLogger(__name__)


def build_shopping_graph(
    *,
    search_agent: SearchAgent | None = None,
    comparison_agent: ComparisonAgent | None = None,
    inventory_agent: InventoryAgent | None = None,
    budget_agent: BudgetAgent | None = None,
    recommendation_agent: RecommendationAgent | None = None,
):
    """Build a fresh workflow; agents can be injected for tests or custom runtimes."""
    workflow = StateGraph(ShoppingState)
    workflow.add_node("search", partial(search_node, agent=search_agent))
    workflow.add_node("comparison", partial(comparison_node, agent=comparison_agent))
    workflow.add_node("inventory", partial(inventory_node, agent=inventory_agent))
    workflow.add_node("budget", partial(budget_node, agent=budget_agent))
    workflow.add_node("recommendation", partial(recommendation_node, agent=recommendation_agent))

    workflow.add_edge(START, "search")
    workflow.add_conditional_edges(
        "search",
        lambda state: "recommendation"
        if state.get("error") or not state.get("search_results", {}).get("matches")
        else "comparison",
        {"comparison": "comparison", "recommendation": "recommendation"},
    )
    workflow.add_edge("comparison", "inventory")
    workflow.add_edge("inventory", "budget")
    workflow.add_edge("budget", "recommendation")
    workflow.add_edge("recommendation", END)

    logger.info("Shopping workflow compiled")
    return workflow.compile()


shopping_graph = build_shopping_graph()


def run_shopping_workflow(user_query: str) -> ShoppingState:
    """Execute the compiled graph for one customer query."""
    logger.info("Shopping workflow started")
    result = shopping_graph.invoke({"user_query": user_query})
    logger.info("Shopping workflow completed")
    return result
