Architecture sketch - RAG-Powered Policy Assistant (v1)

ASCII diagram (pipeline):

  [PDFs (50)]
        |
        v
  Ingest & OCR/parse -> Chunking -> Store chunks + metadata
        |                          |
        |                          v
        |                    Vector DB (pgvector in Postgres)
        v                          |
  Embeddings (sentence-transformers / OpenAI embeddings)
        |
        v
  Retrieval (kNN + metadata filtering) -> Retrieved chunks
        |
        v
  Prompt assembly (system prompt + citations) -> LLM (Claude/Anthropic or OpenAI)
        |
        v
  Answer (structured JSON with inline citations)
        |
        v
  Evals & monitoring (automated tests, human review, logging)


Tech choices and justification (short):
- Storage: Postgres + pgvector — reliable ACID DB we already use, simple ops, scales for more than 50 docs also.
- Embeddings: sentence-transformers (local) or OpenAI embeddings for quality and speed tradeoffs.
- Retrieval: kNN via pgvector + SQL metadata filters (policy_id, effective_date, doc_type).
- LLM / Generation: Claude or OpenAI GPT-4o depending on budget — choose a model with system-prompt control.
- Orchestration: Python (FastAPI later) for easy prototyping and clear types.
- Evals: pytest + LLM-as-judge for synthesis; human checks for ambiguous legal interpretations.
