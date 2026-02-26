from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    doc_name: str
    text: str


def normalize_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(doc_name: str, text: str, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    clean = normalize_text(text)
    if not clean:
        return []

    chunks: list[Chunk] = []
    start = 0
    idx = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        piece = clean[start:end].strip()
        if piece:
            chunks.append(Chunk(chunk_id=f'{doc_name}::chunk_{idx}', doc_name=doc_name, text=piece))
            idx += 1
        if end >= len(clean):
            break
        start = max(0, end - chunk_overlap)
    return chunks
