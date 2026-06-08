"""End-to-end RAG orchestration following the guide specification.

Pipeline:
1. Query embedding
2. Vector DB retrieval (kNN)
3. BM25 fallback if similarity is low
4. Merge and deduplicate
5. Re-rank with Cross Encoder
6. Generate answer
"""
from typing import List, Optional
from .embeddings import EmbeddingService
from .reranker import ReRanker
from .bm25_search import BM25Search
from .store import knn_query
from .generator import generate_answer
from .types import DocumentChunk, AnswerResult


class PolicyAssistant:
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        reranker: Optional[ReRanker] = None,
        bm25: Optional[BM25Search] = None
    ):
        """Initialize the full RAG pipeline."""
        self.embeddings = embedding_service
        self.reranker = reranker
        self.bm25 = bm25
        self.similarity_threshold = 0.5  # if below, use BM25 fallback

    async def retrieve_and_rank(
        self,
        question: str,
        top_k: int = 5
    ) -> List[DocumentChunk]:
        """Retrieve + re-rank pipeline.
        
        1. Embed query
        2. Vector DB search (kNN)
        3. Check similarity threshold
        4. If low, merge with BM25 results
        5. Re-rank with Cross Encoder
        """
        # Step 1: Embed query
        if self.embeddings:
            try:
                query_embedding = self.embeddings.embed_text(question)
            except Exception:
                query_embedding = [0.0] * 1024  # fallback
        else:
            query_embedding = [0.0] * 1024
        
        # Step 2: Vector DB kNN
        db_results = await knn_query(query_embedding, k=top_k * 2)  # get 2x for filtering
        db_chunks = [c for c, _ in db_results]
        db_scores = [s for _, s in db_results]
        
        # Step 3: Check if low similarity (fallback to BM25)
        candidates = db_chunks
        if db_scores and db_scores[0] < self.similarity_threshold:
            if self.bm25:
                bm25_results = self.bm25.search(question, top_k=top_k * 2)
                bm25_chunks = [c for c, _ in bm25_results]
                # Merge and deduplicate by chunk_id
                seen = {c.chunk_id for c in candidates}
                for c in bm25_chunks:
                    if c.chunk_id not in seen:
                        candidates.append(c)
                        seen.add(c.chunk_id)
        
        # Step 4: Re-rank with Cross Encoder
        if self.reranker and len(candidates) > 0:
            try:
                reranked = self.reranker.rerank(question, candidates, top_k=top_k)
                candidates = [c for c, _ in reranked]
            except Exception:
                # fallback: keep original order
                candidates = candidates[:top_k]
        else:
            candidates = candidates[:top_k]
        
        return candidates

    async def answer(self, question: str) -> AnswerResult:
        """Full pipeline: retrieve, rank, generate."""
        try:
            retrieved = await self.retrieve_and_rank(question, top_k=5)
            
            if not retrieved:
                return AnswerResult(
                    answer="I could not find this information in the available policies.",
                    citations=[],
                    conflict=None,
                    confidence="LOW",
                    answer_trace="no_retrieval"
                )
            
            return generate_answer(question, retrieved)
        
        except Exception as e:
            return AnswerResult(
                answer=f"Error processing question: {str(e)}",
                citations=[],
                conflict=None,
                confidence="LOW",
                answer_trace=f"error: {str(e)}"
            )
