from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np


class FaissStore:
    def __init__(self, dim: int) -> None:
        self.index = faiss.IndexFlatIP(dim)
        self.metadata: list[dict] = []

    def add(self, vectors: list[list[float]], metadata: list[dict]) -> None:
        if not vectors:
            return
        arr = np.array(vectors, dtype='float32')
        self.index.add(arr)
        self.metadata.extend(metadata)

    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        q = np.array([vector], dtype='float32')
        scores, ids = self.index.search(q, top_k)
        results: list[dict] = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            meta = self.metadata[idx]
            results.append({**meta, 'score': float(score)})
        return results

    def save(self, index_dir: str) -> None:
        path = Path(index_dir)
        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path / 'faiss.index'))
        (path / 'metadata.json').write_text(json.dumps(self.metadata, ensure_ascii=False, indent=2), encoding='utf-8')

    @classmethod
    def load(cls, index_dir: str) -> 'FaissStore':
        path = Path(index_dir)
        index_path = path / 'faiss.index'
        metadata_path = path / 'metadata.json'
        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(f'Index files not found in {index_dir}')

        index = faiss.read_index(str(index_path))
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        store = cls(dim=index.d)
        store.index = index
        store.metadata = metadata
        return store
