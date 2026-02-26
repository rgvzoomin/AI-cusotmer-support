from __future__ import annotations

import hashlib
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.schemas import AskRequest, AskResponse, Citation, LogOut
from app.crm.mock_crm import MockCRMAdapter
from app.db import crud
from app.db.session import get_db
from app.rag.generator import generate_answer
from app.rag.retriever import retrieve
from app.utils.cache import TTLCache
from app.utils.config import get_settings
from app.utils.rate_limit import InMemoryRateLimiter

router = APIRouter()
settings = get_settings()
cache: TTLCache[dict] = TTLCache(max_size=settings.cache_max_size, ttl_seconds=settings.cache_ttl_seconds)
limiter = InMemoryRateLimiter(limit_per_minute=settings.rate_limit_per_minute)
crm = MockCRMAdapter()


def _sanitize_text(text: str) -> str:
    bad_patterns = ['ignore previous instructions', 'system prompt', 'developer instructions', 'jailbreak']
    cleaned = text
    for pattern in bad_patterns:
        cleaned = cleaned.replace(pattern, '')
    return cleaned.strip()


@router.get('/health')
async def health() -> dict:
    return {'status': 'ok'}


@router.get('/stats')
async def stats(db: Session = Depends(get_db)) -> dict:
    return crud.get_stats(db)


@router.get('/logs', response_model=list[LogOut])
async def logs(limit: int = 50, db: Session = Depends(get_db)) -> list[LogOut]:
    limit = min(max(limit, 1), 200)
    return crud.get_logs(db, limit)


@router.post('/ask', response_model=AskResponse)
async def ask(payload: AskRequest, request: Request, db: Session = Depends(get_db)) -> AskResponse:
    client = request.client.host if request.client else 'anonymous'
    if not limiter.allow(client):
        raise HTTPException(status_code=429, detail='Rate limit exceeded. Try again later.')

    sanitized_q = _sanitize_text(payload.question)
    key = hashlib.sha256(sanitized_q.encode('utf-8')).hexdigest()
    cached = cache.get(key)
    if cached:
        return AskResponse(**cached)

    start = time.perf_counter()
    try:
        retrieval = retrieve(settings.index_dir, sanitized_q, top_k=settings.top_k)
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail='RAG index not found. Run ingestion first.')

    citations = [
        Citation(doc=h['doc_name'], chunk_id=h['chunk_id'], score=h['score'], snippet=h['text'][:200])
        for h in retrieval.items
    ]
    top_score = citations[0].score if citations else 0.0
    confidence = max(0.0, min(1.0, float(top_score)))
    handoff_required = confidence < settings.low_similarity_threshold

    if handoff_required:
        answer = (
            "I have insufficient relevant documentation to answer this confidently. "
            "Please hand this over to a human support specialist."
        )
    else:
        answer = generate_answer(sanitized_q, retrieval.items)

    latency_ms = int((time.perf_counter() - start) * 1000)
    result = {
        'answer': answer,
        'citations': [c.model_dump() for c in citations],
        'confidence': confidence,
        'latency_ms': latency_ms,
        'handoff_required': handoff_required,
    }

    crud.create_interaction(
        db,
        question=sanitized_q,
        answer=answer,
        citations=result['citations'],
        latency_ms=latency_ms,
        confidence=confidence,
        customer_id=payload.customer_id,
        ticket_id=payload.ticket_id,
    )

    if payload.ticket_id:
        note = f"AI response: {answer}\nCitations: {result['citations']}"
        crm.add_note(payload.ticket_id, note)

    cache.set(key, result)
    return AskResponse(**result)
