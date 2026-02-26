from __future__ import annotations

import argparse
import logging
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_texts
from app.rag.vectordb import FaissStore
from app.utils.config import get_settings
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {'.txt', '.md'}:
        return path.read_text(encoding='utf-8', errors='ignore')
    if suffix in {'.html', '.htm'}:
        soup = BeautifulSoup(path.read_text(encoding='utf-8', errors='ignore'), 'html.parser')
        return soup.get_text(separator=' ')
    if suffix == '.pdf':
        reader = PdfReader(str(path))
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    return ''


def ingest_docs(docs_dir: str, index_dir: str) -> None:
    settings = get_settings()
    docs_path = Path(docs_dir)
    files = [p for p in docs_path.glob('**/*') if p.is_file() and p.suffix.lower() in {'.pdf', '.txt', '.md', '.html', '.htm'}]
    if not files:
        raise FileNotFoundError(f'No supported documents found in {docs_dir}')

    all_chunks: list[dict] = []
    for fp in files:
        text = _read_file(fp)
        chunks = chunk_text(fp.name, text, settings.chunk_size, settings.chunk_overlap)
        all_chunks.extend([{'doc_name': c.doc_name, 'chunk_id': c.chunk_id, 'text': c.text} for c in chunks])

    if not all_chunks:
        raise RuntimeError('No chunks generated from documents.')

    embeddings = embed_texts([c['text'] for c in all_chunks])
    store = FaissStore(dim=len(embeddings[0]))
    store.add(embeddings, all_chunks)
    store.save(index_dir)
    logger.info('Ingested %s chunks from %s files into %s', len(all_chunks), len(files), index_dir)


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description='Ingest docs and build FAISS index')
    parser.add_argument('--docs', default='./data/docs', help='Path to docs folder')
    parser.add_argument('--index', default='./data/index', help='Path to persist FAISS index')
    args = parser.parse_args()
    ingest_docs(args.docs, args.index)


if __name__ == '__main__':
    main()
