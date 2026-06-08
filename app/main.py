"""Orchestration example for RAG retrieval + generation.

This file shows the high-level flow and error handling paths. It's runnable as a script
but will raise NotImplementedError for external integrations.
"""
from typing import List
from .ingest import chunk_text, parse_pdf_to_text, embed_chunks
from .retriever import InMemoryVectorStore, retrieve
from .generator import generate_answer, call_llm
from .types import DocumentChunk, AnswerResult


def index_policy_text(policy_id: str, source: str, text: str, store: InMemoryVectorStore):
    # Chunk the text
    chunks = chunk_text(text, policy_id=policy_id, source=source)
    # Get embeddings (this will raise NotImplementedError until implemented)
    try:
        embed_chunks(chunks)
    except NotImplementedError:
        # For skeleton, we attach toy embeddings (very small) to allow local testing.
        for i, c in enumerate(chunks):
            c.embedding = [0.0, 0.0, float(i + 1)]
    # Add to store
    for c in chunks:
        store.add(c, c.embedding)


def answer_query(query: str, store: InMemoryVectorStore) -> AnswerResult:
    # In production: compute query embedding via embedding service
    # For skeleton: use simple mock embedding
    query_embedding = [0.0, 0.0, 1.0]
    retrieved = retrieve(store, query_embedding, k=5)
    if len(retrieved.chunks) == 0:
        return AnswerResult(answer="I don't know — the requested information is not present in the policy documents provided.", citations=[], conflict=None, confidence="low", answer_trace="no_retrieved_chunks")
    # Call generator
    try:
        return generate_answer(query, retrieved.chunks)
    except NotImplementedError:
        # When LLM is not integrated, return a traceable stub answer using retrieved text
        citations = []
        for c in retrieved.chunks:
            citations.append({"policy_id": c.policy_id, "source": c.source, "page": c.page, "quote": c.text[:200]})
        return AnswerResult(answer=f"[STUB] Found {len(retrieved.chunks)} chunks. Replace with real LLM.", citations=citations, conflict=None, confidence="low", answer_trace="stub_llm")


def _demo_populate(store: InMemoryVectorStore):
    # Mock policy snippets (2-3 small policies)
    p1 = "Daily per-diem for international travel is $75USD for meals and $150USD for incidentals. Employees must submit receipts over $25."
    p2 = "Employees may use personal laptops only if endpoint security is installed and IT approval is granted. No corporate data should be stored on personal devices."
    index_policy_text("HR-EXPENSES-001", "hr_expenses.pdf", p1, store)
    index_policy_text("IT-SHARED-002", "it_security.pdf", p2, store)


def main():
    store = InMemoryVectorStore()
    _demo_populate(store)
    q = "What's the daily expense limit for international travel?"
    ans = answer_query(q, store)
    print("Answer:", ans.answer)
    print("Citations:", ans.citations)


if __name__ == "__main__":
    main()
