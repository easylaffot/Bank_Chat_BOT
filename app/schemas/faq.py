"""Pydantic response model for grounded FAQ answers."""

from pydantic import BaseModel, ConfigDict, Field


class FAQAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1)
    sources: list[str]
