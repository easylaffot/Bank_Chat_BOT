"""Pydantic response model for grounded FAQ answers."""

from pydantic import BaseModel, ConfigDict, Field


class FAQQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=2000)


class FAQAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1)
    sources: list[str]
