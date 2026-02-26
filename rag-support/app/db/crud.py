from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import InteractionLog


def create_interaction(
    db: Session,
    *,
    question: str,
    answer: str,
    citations: list[dict],
    latency_ms: int,
    confidence: float,
    customer_id: str | None = None,
    ticket_id: str | None = None,
) -> InteractionLog:
    row = InteractionLog(
        question=question,
        answer=answer,
        citations_json=json.dumps(citations, ensure_ascii=False),
        latency_ms=latency_ms,
        confidence=confidence,
        customer_id=customer_id,
        ticket_id=ticket_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_logs(db: Session, limit: int = 50) -> list[InteractionLog]:
    stmt = select(InteractionLog).order_by(InteractionLog.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())


def get_stats(db: Session) -> dict:
    total_queries = db.scalar(select(func.count(InteractionLog.id))) or 0

    cutoff = datetime.utcnow() - timedelta(hours=24)
    last_24h = db.scalar(select(func.count(InteractionLog.id)).where(InteractionLog.created_at >= cutoff)) or 0

    avg_latency = db.scalar(select(func.avg(InteractionLog.latency_ms))) or 0.0
    avg_confidence = db.scalar(select(func.avg(InteractionLog.confidence))) or 0.0

    return {
        'total_queries': int(total_queries),
        'last_24h_count': int(last_24h),
        'avg_latency_ms': float(round(avg_latency, 2)),
        'avg_confidence': float(round(avg_confidence, 4)),
    }
