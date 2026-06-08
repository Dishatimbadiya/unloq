"""Retrieval layer and a simple in-memory vector store for development/testing.

Replace the in-memory store with Postgres + pgvector in production.
"""
from typing import List, Tuple, Optional
from .types import DocumentChunk, RetrievalResult
import math


class InMemoryVectorStore:
    def __init__(self):
        # store tuples of (chunk, embedding)
        self._store: List[Tuple[DocumentChunk, List[float]]] = []

    def add(self, chunk: DocumentChunk, embedding: List[float]):
        if embedding is None:
            raise ValueError("Embedding must be provided")
        self._store.append((chunk, embedding))

    def knn(self, query_embedding: List[float], k: int = 5) -> RetrievalResult:
        # naive cosine similarity
        def dot(a, b):
            return sum(x * y for x, y in zip(a, b))

        def norm(a):
            return math.sqrt(sum(x * x for x in a))

        results = []
        for chunk, emb in self._store:
            if len(emb) != len(query_embedding):
                continue
            score = dot(emb, query_embedding) / (norm(emb) * norm(query_embedding) + 1e-9)
            results.append((score, chunk))
        results.sort(key=lambda x: x[0], reverse=True)
        top = results[:k]
        return RetrievalResult(chunks=[c for s, c in top], scores=[s for s, c in top])


def retrieve(context_store: InMemoryVectorStore, query_embedding: List[float], k: int = 5) -> RetrievalResult:
    return context_store.knn(query_embedding, k=k)
