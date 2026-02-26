from __future__ import annotations

import json
from pathlib import Path

from app.rag.embeddings import embed_query
from app.rag.retriever import retrieve
from app.utils.config import get_settings


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return float(sum(x * y for x, y in zip(a, b)))


def main(dataset_path: str, k: int = 5) -> None:
    settings = get_settings()
    rows = [json.loads(line) for line in Path(dataset_path).read_text(encoding='utf-8').splitlines() if line.strip()]

    hit = 0
    quality_scores: list[float] = []

    for row in rows:
        question = row['question']
        hits = retrieve(settings.index_dir, question, top_k=k).items

        expected_doc = row.get('expected_doc')
        if expected_doc and any(expected_doc == h['doc_name'] for h in hits):
            hit += 1

        expected_keywords = row.get('expected_keywords', [])
        joined = ' '.join(h['text'] for h in hits[:2]).lower()
        if expected_keywords:
            matched = sum(1 for kw in expected_keywords if kw.lower() in joined)
            quality_scores.append(matched / len(expected_keywords))
        else:
            q_vec = embed_query(question)
            ctx_vec = embed_query(joined[:1000] if joined else question)
            quality_scores.append(max(0.0, min(1.0, cosine_similarity(q_vec, ctx_vec))))

    report = {
        'samples': len(rows),
        'retrieval_hit_at_k': round(hit / len(rows), 4) if rows else 0.0,
        'avg_quality_proxy': round(sum(quality_scores) / len(quality_scores), 4) if quality_scores else 0.0,
    }

    out = Path('./data/eval_report.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')

    print('Evaluation Summary')
    print(f"- Samples: {report['samples']}")
    print(f"- Retrieval hit@{k}: {report['retrieval_hit_at_k']}")
    print(f"- Avg quality proxy: {report['avg_quality_proxy']}")
    print(f'- Report written to: {out}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate RAG retrieval and answer proxy quality')
    parser.add_argument('--dataset', required=True, help='JSONL file with evaluation samples')
    parser.add_argument('--k', type=int, default=5)
    args = parser.parse_args()
    main(args.dataset, args.k)
