from __future__ import annotations

from dataclasses import dataclass

from app.rag.embeddings import embed_query
from app.rag.vectordb import FaissStore


@dataclass
class RetrievalResult:
    items: list[dict]


def retrieve(index_dir: str, question: str, top_k: int = 5) -> RetrievalResult:
    store = FaissStore.load(index_dir)
    qv = embed_query(question)
    hits = store.search(qv, top_k=top_k)
    return RetrievalResult(items=hits)
