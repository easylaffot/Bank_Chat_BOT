"""Typed shared state for the LangGraph shopping workflow."""

from typing import Any, TypedDict


class WorkflowError(TypedDict):
    code: str
    message: str


class ShoppingState(TypedDict, total=False):
    user_query: str
    search_results: dict[str, Any]
    comparison_results: list[dict[str, Any]]
    inventory_results: dict[str, dict[str, Any]]
    budget_results: dict[str, Any]
    recommendation: dict[str, Any]
    error: WorkflowError | None
