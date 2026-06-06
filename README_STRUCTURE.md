# Unloq Policy Assistant (v1) — Production RAG

A **complete, production-grade RAG (Retrieval-Augmented Generation)** system for policy Q&A.

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration

Copy and edit `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/unloq
PGVECTOR_DIM=1024

# Models
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
RERANKER_MODEL=cross-encoder/msl-mcd6

# LLM
LLM_PROVIDER=anthropic  # or openai
ANTHROPIC_API_KEY=your_key_here

# Service
LOG_LEVEL=INFO
```

### 3. Database Setup

```bash
python scripts/setup_db.py
```

### 4. Start Server

```bash
uvicorn api.main:app --reload --port 8000
```

### 5. Ingest Policies

```bash
python scripts/ingest_policy.py /path/to/policy.pdf POL-HR-001
```

### 6. Query

```bash
python scripts/query_policy.py "What is the travel limit?"
```

Or via HTTP:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the travel limit?"}'
```

---

## Project Structure

```
unloq_policy_assistant/
│
├── src/unloq_rag/             # Main RAG package
│   ├── core/                  # Shared types & exceptions
│   │   ├── types.py           # DocumentChunk, AnswerResult
│   │   └── exceptions.py      # RAGError, PDFParseError, etc.
│   │
│   ├── ingestion/             # PDF parsing & chunking
│   │   ├── pdf_parser.py      # PyMuPDF extraction
│   │   └── chunker.py         # Text chunking (500-char with overlap)
│   │
│   ├── retrieval/             # Search & ranking
│   │   ├── embeddings.py      # BAAI/bge-large embeddings
│   │   ├── vector_store.py    # Postgres + pgvector KNN
│   │   ├── reranker.py        # Cross Encoder re-ranking
│   │   └── bm25_search.py     # Keyword fallback search
│   │
│   ├── generation/            # LLM prompting
│   │   └── generator.py       # Prompt assembly + parsing
│   │
│   ├── storage/               # Database layer
│   │   └── db.py              # SQLAlchemy models + SessionLocal
│   │
│   └── orchestration/         # End-to-end pipeline
│       └── orchestrator.py    # PolicyAssistant class
│
├── api/                       # FastAPI HTTP service
│   └── main.py                # Endpoints: /ingest, /query, /health
│
├── config/                    # Configuration
│   └── settings.py            # Pydantic BaseSettings
│
├── tests/                     # Test suite
│   ├── conftest.py            # Pytest configuration & fixtures
│   ├── test_retrieval.py      # Retrieval tests
│   ├── test_generation.py     # Generation tests
│   └── test_evals.py          # Eval spec tests
│
├── scripts/                   # CLI helpers
│   ├── ingest_policy.py       # Ingest a PDF
│   ├── query_policy.py        # Query the assistant
│   └── setup_db.py            # Initialize DB schema
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # Tech choices & justification
│   ├── IMPLEMENTATION_GUIDE.md # Full implementation details
│   ├── FAILURE_RECOVERY.md    # Failure modes & monitoring
│   ├── PROMPT_ENGINEERING.md  # System prompt details
│   └── EVALS.md               # Six evaluation cases
│
├── mocks/                     # Example data
│   └── policy_snippets.md     # Sample policy texts
│
├── .env                       # Environment (git-ignored)
├── .env.example               # Example env template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Architecture

```
Query → Embed → Vector DB KNN → Similarity Check
                    ↓
              < 0.5? → BM25 Fallback → Merge Results
                    ↓
              Re-rank (Cross Encoder) → Top-5
                    ↓
              LLM Generation + Citations
                    ↓
              Structured Answer (JSON)
```

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Ingestion** | PyMuPDF | Enterprise PDF support + page preservation |
| **Embeddings** | BAAI/bge-large (1024D) | Open-source, competitive quality, efficient |
| **Vector DB** | Postgres + pgvector | Reliable ACID DB, simple ops, scales to 1M+ |
| **Re-ranker** | Cross Encoder (MiniLM) | +20% precision vs bi-encoder alone |
| **Search Fallback** | BM25 (rank-bm25) | Keyword-based when semantic similarity low |
| **LLM** | Claude/GPT-4o (stubbed) | Strong instruction following + grounding |
| **Framework** | FastAPI | Modern, async-friendly, production-ready |

---

## API Endpoints

### `POST /health`
Check component status.

```json
{
  "status": "ok",
  "components": {
    "embeddings": true,
    "reranker": true,
    "bm25": true,
    "assistant": true
  }
}
```

### `POST /ingest`
Ingest a policy document.

**Request:**
```json
{
  "policy_id": "POL-FIN-001",
  "source": "finance_policy.pdf",
  "text": "Daily per-diem for international travel is $150..."
}
```

**Response:**
```json
{
  "status": "ok",
  "policy_id": "POL-FIN-001",
  "ingested_chunks": 12,
  "total_text_chars": 5432
}
```

### `POST /query`
Query the assistant.

**Request:**
```json
{
  "question": "What is the daily travel limit?",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "The daily international travel limit is $150/day. [POL-FIN-001]",
  "confidence": "HIGH",
  "citations": [
    {"policy_id": "POL-FIN-001", "source": "finance_policy.pdf", "page": 3}
  ],
  "conflict": null,
  "answer_trace": null
}
```

---

## Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_evals.py

# With coverage
pytest --cov=src tests/
```

---

## Scripts

### Ingest a policy
```bash
python scripts/ingest_policy.py /path/to/policy.pdf POL-ID
```

### Query assistant
```bash
python scripts/query_policy.py "Your question here?"
```

### Setup database
```bash
python scripts/setup_db.py
```

---

## Configuration

All settings from `.env`:

```bash
# Core
DATABASE_URL=postgresql+asyncpg://...
PGVECTOR_DIM=1024

# Embeddings
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# Retrieval
RETRIEVAL_TOP_K=5
SIMILARITY_THRESHOLD=0.5

# Re-ranker
RERANKER_MODEL=cross-encoder/msl-mcd6
RERANKER_TOP_K=3

# BM25
USE_BM25_FALLBACK=true

# LLM
LLM_PROVIDER=anthropic|openai
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...

# Logging
LOG_LEVEL=INFO|DEBUG
```

---

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Tech choices & system design
- **[IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)** — Complete module walkthrough
- **[PROMPT_ENGINEERING.md](docs/PROMPT_ENGINEERING.md)** — System prompt design
- **[EVALS.md](docs/EVALS.md)** — Six evaluation test cases
- **[FAILURE_RECOVERY.md](docs/FAILURE_RECOVERY.md)** — Failure modes & monitoring

---

## Production Checklist

- [ ] LLM integration (wire Claude/GPT-4o in `generator.py`)
- [ ] Postgres + pgvector setup & pgvector extension enabled
- [ ] Embedding model downloaded (BAAI/bge-large)
- [ ] Re-ranker model ready (cross-encoder/msl-mcd6)
- [ ] Database indexes on `policy_chunks.embedding`
- [ ] Run full eval suite in `tests/`
- [ ] Rate limiting on `/query` endpoint
- [ ] Structured logging with trace_id
- [ ] Monitoring: retrieval scores, latency, error rates
- [ ] Policy owner assignment + versioning

---

## Failure Modes & Recovery

See [FAILURE_RECOVERY.md](docs/FAILURE_RECOVERY.md) for:

1. **Wrong Retrieval** → Threshold check + BM25 fallback
2. **Stale Policies** → Timestamp monitoring + auto re-index
3. **Conflicting Policies** → Conflict detection + policy owner alert

---

## License

Unloq Solutions Ltd | Confidential
