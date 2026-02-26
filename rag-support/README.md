# AI-Powered Customer Support System (RAG)

Production-style Retrieval-Augmented Generation (RAG) support assistant with:
- FastAPI async service
- FAISS local vector search
- Sentence-transformers embeddings
- OpenAI-compatible LLM with safe local fallback
- SQLite/SQLAlchemy interaction logging
- Mock CRM adapter
- Streamlit test UI
- Evaluation script for retrieval + answer quality proxy

## Project Structure

```text
rag-support/
  app/
  data/
  scripts/
  tests/
  ui/
  eval.py
```

## 1) Setup

```bash
cd rag-support
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 2) Add Documents

Put your docs under `./data/docs`.
Supported formats:
- PDF
- TXT
- MD
- HTML

## 3) Build the Index (Ingestion)

```bash
python -m app.rag.ingest --docs ./data/docs --index ./data/index
```

This command:
- parses supported docs
- normalizes and chunks text
- creates embeddings
- writes FAISS index + metadata to `./data/index/`

## 4) Start the API

```bash
export PYTHONPATH=.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

or

```bash
./scripts/run_dev.sh
```

## 5) Ask a Support Question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How can I reset my password?",
    "customer_id": "cust-123",
    "ticket_id": "TICK-22"
  }'
```

Expected response fields:
- `answer`
- `citations` (doc/chunk/score/snippet)
- `confidence`
- `latency_ms`
- `handoff_required`

## 6) Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

## 7) Evaluation

Prepare JSONL dataset, each line like:

```json
{"question":"How do I reset password?","expected_keywords":["reset","password"],"expected_doc":"faq.md"}
```

Run:

```bash
python eval.py --dataset ./data/eval_dataset.jsonl --k 5
```

Outputs report to `./data/eval_report.json`.

## API Endpoints

- `GET /health`
- `GET /stats`
- `GET /logs?limit=50`
- `POST /ask`

## Performance and Safety Notes (10k+ queries/day)

- Use multiple workers in production:
  - `gunicorn -k uvicorn.workers.UvicornWorker -w 4 app.main:app`
- Keep FAISS index in local SSD-backed storage.
- Enable memory cache (included TTL LRU) for repeated queries.
- Use async API handlers and lightweight in-memory rate limiting.
- Add Postgres + connection pooling for higher logging throughput.
- Consider background logging queue for burst traffic.
- Prompt injection safeguards:
  - sanitize common override phrases
  - system prompt enforces context-only policy
- Low similarity handling triggers explicit human handoff recommendation.

## Docker

```bash
docker compose up --build
```

## Testing

```bash
pytest -q
```
