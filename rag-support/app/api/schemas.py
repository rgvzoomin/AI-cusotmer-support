from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    customer_id: str | None = Field(default=None, max_length=255)
    ticket_id: str | None = Field(default=None, max_length=255)


class Citation(BaseModel):
    doc: str
    chunk_id: str
    score: float
    snippet: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
    latency_ms: int
    handoff_required: bool


class LogOut(BaseModel):
    id: int
    customer_id: str | None
    ticket_id: str | None
    question: str
    answer: str
    citations_json: str
    latency_ms: int
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True
