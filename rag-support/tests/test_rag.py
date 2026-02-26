from app.rag.chunking import chunk_text


def test_chunking_creates_chunks() -> None:
    text = 'A' * 2500
    chunks = chunk_text('doc.txt', text, chunk_size=1000, chunk_overlap=100)
    assert len(chunks) >= 2
    assert chunks[0].chunk_id.startswith('doc.txt::chunk_')
