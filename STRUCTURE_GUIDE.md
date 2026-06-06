# Project Structure Guide

## Overview

The project is organized into **clear, modular layers** for easy navigation and maintenance.

## Top-Level Organization

```
unloq_policy_assistant/
├── src/unloq_rag/       ← Core RAG package (business logic)
├── api/                 ← FastAPI HTTP service layer
├── config/              ← Configuration management
├── tests/               ← Test suite (unit + evals)
├── scripts/             ← CLI helper scripts
├── docs/                ← Documentation
├── mocks/               ← Sample data
└── [config files]
```

---

## **1. Core Package: `src/unloq_rag/`**

The main RAG implementation split into 6 logical modules:

### **1.1 Core Module** (`core/`)
**Shared types and exceptions across all modules.**

Files:
- `types.py` — Core dataclasses
  - `DocumentChunk` — Policy text chunk with embedding
  - `RetrievalResult` — Search results with scores
  - `AnswerResult` — Final structured answer
- `exceptions.py` — Custom exceptions (RAGError, PDFParseError, etc.)

**Use:** Import shared types from here in all modules.

```python
from src.unloq_rag.core import DocumentChunk, AnswerResult
```

---

### **1.2 Ingestion Module** (`ingestion/`)
**PDF parsing and chunking.**

Files:
- `pdf_parser.py` (PyMuPDF)
  - `extract_text_with_pages()` — Get text with page numbers
  - `extract_full_text()` — Get full PDF as string
- `chunker.py`
  - `chunk_text()` — Split text into overlapping chunks (500 chars)

**Use:** Ingest policies into the system.

```python
from src.unloq_rag.ingestion import extract_full_text, chunk_text

text = extract_full_text("policy.pdf")
chunks = chunk_text(text, policy_id="POL-001", source="policy.pdf")
```

---

### **1.3 Retrieval Module** (`retrieval/`)
**Semantic search, re-ranking, keyword fallback.**

Files:
- `embeddings.py` (BAAI/bge-large)
  - `EmbeddingService.embed_text()` — Embed single text
  - `EmbeddingService.embed_texts()` — Batch embedding
- `vector_store.py` (Postgres + pgvector)
  - `knn_query()` — KNN search in vector DB
  - `upsert_chunks()` — Store chunks with embeddings
- `reranker.py` (Cross Encoder)
  - `ReRanker.rerank()` — Re-rank candidates by relevance
- `bm25_search.py` (rank-bm25)
  - `BM25Search.search()` — Keyword-based fallback

**Use:** Retrieve and rank relevant policy chunks.

```python
from src.unloq_rag.retrieval import EmbeddingService, ReRanker, knn_query

emb = EmbeddingService()
query_vec = emb.embed_text("What is the travel limit?")
chunks = await knn_query(query_vec, k=5)
```

---

### **1.4 Generation Module** (`generation/`)
**LLM prompting and answer parsing.**

Files:
- `generator.py`
  - `SYSTEM_PROMPT` — Strict markdown-format prompt
  - `assemble_prompt()` — Build full prompt with context
  - `call_llm()` — Call LLM (stubbed until integrated)
  - `parse_markdown_answer()` — Parse LLM markdown output
  - `generate_answer()` — Full generation pipeline

**Use:** Generate grounded answers with citations.

```python
from src.unloq_rag.generation import generate_answer

result = generate_answer("What's the travel limit?", chunks)
print(result.answer)  # "The limit is $150/day [POL-FIN-001]"
print(result.confidence)  # "HIGH"
```

---

### **1.5 Storage Module** (`storage/`)
**Database models and initialization.**

Files:
- `db.py`
  - `PolicyChunk` — SQLAlchemy model (pgvector column)
  - `init_db()` — Create tables
  - `async_session` — Session factory

**Use:** Database layer (imported by retrieval module).

```python
from src.unloq_rag.storage import PolicyChunk, init_db
```

---

### **1.6 Orchestration Module** (`orchestration/`)
**End-to-end RAG pipeline.**

Files:
- `orchestrator.py`
  - `PolicyAssistant` class
    - `__init__()` — Inject embedding, re-ranker, BM25
    - `retrieve_and_rank()` — Full retrieval pipeline
    - `answer()` — Full RAG: retrieve → rank → generate

**Use:** Main entry point for queries.

```python
from src.unloq_rag.orchestration import PolicyAssistant

assistant = PolicyAssistant(
    embedding_service=emb,
    reranker=reranker,
    bm25=bm25,
    similarity_threshold=0.5
)
result = await assistant.answer("What's the travel limit?")
```

---

## **2. API Layer: `api/`**

FastAPI HTTP service exposing the RAG system.

Files:
- `main.py`
  - `startup()` — Initialize all components
  - `GET /health` — Component status
  - `POST /ingest` — Ingest policy
  - `POST /query` — Query assistant

**Use:** Start server with:
```bash
uvicorn api.main:app --reload --port 8000
```

---

## **3. Configuration: `config/`**

Centralized settings management.

Files:
- `settings.py` (Pydantic BaseSettings)
  - Loads from `.env`
  - Provides `settings` singleton
  - All config in one place

**Use:**
```python
from config import settings

print(settings.database_url)
print(settings.embedding_model)
```

---

## **4. Tests: `tests/`**

Test suite split by module.

Files:
- `conftest.py` — Pytest fixtures (mock chunks, embeddings)
- `test_retrieval.py` — BM25, vector search tests
- `test_generation.py` — Prompt assembly, parsing
- `test_evals.py` — Six eval cases from evals.md

**Use:**
```bash
pytest tests/
pytest tests/test_evals.py -v
```

---

## **5. Scripts: `scripts/`**

CLI helpers for common operations.

Files:
- `setup_db.py` — Initialize database schema
- `ingest_policy.py` — Ingest a single PDF
- `query_policy.py` — Query assistant from CLI

**Use:**
```bash
python scripts/setup_db.py
python scripts/ingest_policy.py /path/to/policy.pdf POL-ID
python scripts/query_policy.py "Your question?"
```

---

## **6. Documentation: `docs/`**

Complete reference documentation.

Files:
- `ARCHITECTURE.md` — System design & tech choices
- `IMPLEMENTATION_GUIDE.md` — Module walkthrough
- `PROMPT_ENGINEERING.md` — System prompt details
- `EVALS.md` — Six evaluation test cases
- `FAILURE_RECOVERY.md` — Failure modes & monitoring

---

## **7. Mocks: `mocks/`**

Example data for testing.

Files:
- `policy_snippets.md` — Three sample policies (HR, IT, Finance)

---

## Navigation Tips

### Finding a Function
1. **Search in `src/unloq_rag/`** by module purpose:
   - PDF parsing → `ingestion/pdf_parser.py`
   - Embeddings → `retrieval/embeddings.py`
   - DB queries → `retrieval/vector_store.py`
   - LLM calls → `generation/generator.py`
   - Full pipeline → `orchestration/orchestrator.py`

2. **Check imports** — Each module's `__init__.py` lists public APIs

### Adding a Feature
1. **If it's a new data type** → Add to `core/types.py`
2. **If it's PDF-related** → Add to `ingestion/`
3. **If it's search-related** → Add to `retrieval/`
4. **If it's LLM-related** → Add to `generation/`
5. **If it orchestrates steps** → Update `orchestration/orchestrator.py`
6. **If it's a new endpoint** → Add to `api/main.py`

---

## Module Dependencies

```
api/main.py
    ↓
orchestration/orchestrator.py
    ├→ retrieval/*.py (embeddings, reranker, bm25, vector_store)
    ├→ generation/generator.py
    ├→ storage/db.py
    └→ core/*.py

retrieval/*.py
    └→ core/*.py
    
generation/generator.py
    └→ core/*.py

ingestion/*.py
    └→ core/*.py

storage/db.py
    └→ core/*.py
```

**Key principle:** Core types are shared, modules are independent.

---

## Quick Reference

| Need | File | Function |
|------|------|----------|
| Extract PDF | `ingestion/pdf_parser.py` | `extract_full_text()` |
| Split text | `ingestion/chunker.py` | `chunk_text()` |
| Embed text | `retrieval/embeddings.py` | `EmbeddingService.embed_texts()` |
| Search vectors | `retrieval/vector_store.py` | `knn_query()` |
| Keyword search | `retrieval/bm25_search.py` | `BM25Search.search()` |
| Re-rank | `retrieval/reranker.py` | `ReRanker.rerank()` |
| Generate answer | `generation/generator.py` | `generate_answer()` |
| Full pipeline | `orchestration/orchestrator.py` | `PolicyAssistant.answer()` |
| HTTP endpoints | `api/main.py` | `/ingest`, `/query` |
| Settings | `config/settings.py` | `settings` object |
