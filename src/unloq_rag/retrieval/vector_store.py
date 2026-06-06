"""Vector database adapter for Postgres + pgvector."""
from typing import List, Tuple
import math
from sqlalchemy import select
from ..core import DocumentChunk
from ..storage.db import async_session, PolicyChunk


async def upsert_chunks(chunks: List[DocumentChunk]):
    """Upsert chunks into vector DB.
    
    Args:
        chunks: policy chunks with embeddings
    """
    import uuid
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


def _cosine_distance(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between vectors."""
    if a is None or b is None:
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return -1.0
    return dot / (na * nb)


async def knn_query(
    query_embedding: List[float],
    k: int = 5
) -> List[Tuple[PolicyChunk, float]]:
    """Retrieve top-k chunks by similarity.
    
    Note: This is a Python-side fallback. For production >100k chunks,
    use pgvector's native KNN operator in SQL.
    
    Args:
        query_embedding: query embedding vector
        k: number of results to return
    
    Returns:
        List of (chunk, score) sorted by similarity descending
    """
    async with async_session() as session:
        q = await session.execute(select(PolicyChunk))
        rows = q.scalars().all()
    
    scored = []
    for r in rows:
        score = _cosine_distance(r.embedding, query_embedding) if r.embedding else -1.0
        scored.append((r, score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
