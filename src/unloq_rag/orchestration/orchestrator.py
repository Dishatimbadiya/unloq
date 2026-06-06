"""End-to-end RAG orchestration: retrieval + ranking + generation."""
from typing import List, Optional
from ..core import DocumentChunk, AnswerResult
from ..retrieval import EmbeddingService, ReRanker, BM25Search, knn_query
from ..generation import generate_answer


class PolicyAssistant:
    """Full RAG pipeline orchestrator."""
    
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        reranker: Optional[ReRanker] = None,
        bm25: Optional[BM25Search] = None,
        similarity_threshold: float = 0.5
    ):
        """Initialize RAG assistant.
        
        Args:
            embedding_service: embedding model for query encoding
            reranker: Cross Encoder for precision improvement
            bm25: BM25 search for keyword fallback
            similarity_threshold: trigger BM25 fallback below this score
        """
        self.embeddings = embedding_service
        self.reranker = reranker
        self.bm25 = bm25
        self.similarity_threshold = similarity_threshold
    
    async def retrieve_and_rank(
        self,
        question: str,
        top_k: int = 5
    ) -> List[DocumentChunk]:
        """Retrieve + re-rank pipeline.
        
        Steps:
        1. Embed query
        2. Vector DB kNN search
        3. Check similarity threshold
        4. If low, merge with BM25 results
        5. Re-rank with Cross Encoder
        
        Args:
            question: user question
            top_k: target number of results
        
        Returns:
            Re-ranked list of retrieved chunks
        """
        # Step 1: Embed query
        if self.embeddings:
            try:
                query_embedding = self.embeddings.embed_text(question)
            except Exception:
                query_embedding = [0.0] * 1024  # fallback
        else:
            query_embedding = [0.0] * 1024
        
        # Step 2: Vector DB kNN (get 2x for filtering)
        db_results = await knn_query(query_embedding, k=top_k * 2)
        db_chunks = [c for c, _ in db_results]
        db_scores = [s for _, s in db_results]
        
        # Step 3: Check similarity threshold
        candidates = db_chunks
        if db_scores and db_scores[0] < self.similarity_threshold:
            # Step 3b: Fallback to BM25
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
                # fallback: keep current order
                candidates = candidates[:top_k]
        else:
            candidates = candidates[:top_k]
        
        return candidates
    
    async def answer(self, question: str) -> AnswerResult:
        """Full pipeline: retrieve → rank → generate.
        
        Args:
            question: user question
        
        Returns:
            Structured answer with citations
        """
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
