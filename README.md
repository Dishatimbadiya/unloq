RAG-Powered Policy Assistant - v1 (Production Grade)

This folder contains a complete RAG pipeline for policy Q&A with:
- PDF parsing (PyMuPDF)
- Embeddings (BAAI/bge-large-en-v1.5)
- Vector DB (Postgres + pgvector)
- Re-ranker (Cross Encoder)
- BM25 fallback (hybrid search)
- FastAPI service

Quick start:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set DATABASE_URL in .env or environment:

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/unloq"
```

3. Start the FastAPI server:

```bash
uvicorn unloq_policy_assistant.app.main_fastapi:app --reload --port 8000
```

Endpoints:
- `POST /health` — check components
- `POST /ingest` — chunk + embed + store policy
- `POST /query` — retrieve + rank + generate answer

Full guide: see IMPLEMENTATION_GUIDE.md
