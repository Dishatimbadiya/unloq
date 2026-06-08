"""DB adapter: upsert chunks and a simple KNN retrieval fallback.

Note: Production should use pgvector KNN queries for efficiency. This file stores
embeddings in the pgvector column and provides a small-scale Python-side similarity
fallback when the DB-side operator is not used.
"""
from typing import List, Iterable, Optional, Tuple
import uuid
from .db import async_session, PolicyChunk
from .types import DocumentChunk
from sqlalchemy import select
import math


async def upsert_chunks(chunks: Iterable[DocumentChunk]):
    async with async_session() as session:
        async with session.begin():
            for c in chunks:
                obj = PolicyChunk(
                    id=str(uuid.uuid4()),
                    policy_id=c.policy_id,
                    source=c.source,
                    page=c.page if c.page is not None else None,
                    chunk_id=c.chunk_id,
                    text=c.text,
                    embedding=c.embedding,
                )
                session.add(obj)


def _cosine(a: List[float], b: List[float]) -> float:
    if a is None or b is None:
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return -1.0
    return dot / (na * nb)


async def knn_query(query_embedding: List[float], k: int = 5) -> List[Tuple[PolicyChunk, float]]:
    """Return top-k chunks and similarity scores.

    This implementation fetches all rows and computes similarity in Python. It's
    acceptable for a small corpus (50 policies). Replace with a DB KNN query for scale.
    """
    async with async_session() as session:
        q = await session.execute(select(PolicyChunk))
        rows = q.scalars().all()
    scored = []
    for r in rows:
        score = _cosine(r.embedding, query_embedding) if r.embedding is not None else -1.0
        scored.append((r, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
