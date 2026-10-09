"""Request and response models for the shopping assistant workflow API."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ShoppingAssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=2000)


class ShoppingAssistantError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str


class ShoppingAssistantResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendation: dict[str, Any] | None = None
    alternatives: list[dict[str, Any]] = Field(default_factory=list)
    error: ShoppingAssistantError | None = None
