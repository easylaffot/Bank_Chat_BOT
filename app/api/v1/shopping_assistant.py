"""HTTP endpoint for the graph-driven shopping assistant."""

import logging

from fastapi import APIRouter

from app.schemas.shopping_assistant import (
    ShoppingAssistantRequest,
    ShoppingAssistantResponse,
)
from app.services.shopping_assistant_service import ShoppingAssistantService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/shopping-assistant", tags=["Shopping Assistant"])
_service = ShoppingAssistantService()


@router.post("", response_model=ShoppingAssistantResponse)
def create_shopping_recommendation(
    request: ShoppingAssistantRequest,
) -> ShoppingAssistantResponse:
    logger.info("Shopping assistant endpoint called")
    return ShoppingAssistantResponse.model_validate(_service.execute(request.query))
