"""Re-ranker using Cross Encoder (MiniLM) to improve retrieval precision.

Cross Encoders are more accurate than embeddings for ranking pairs.
They compare question + candidate directly, yielding better precision.
"""
from typing import List, Tuple
from sentence_transformers import CrossEncoder
from .types import DocumentChunk


class ReRanker:
    def __init__(self, model_name: str = "cross-encoder/miniln-l6-mcd6"):
        """Initialize Cross Encoder model."""
        try:
            self.model = CrossEncoder(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load reranker model: {e}")
    
    def rerank(
        self,
        question: str,
        chunks: List[DocumentChunk],
        top_k: int = 3
    ) -> List[Tuple[DocumentChunk, float]]:
        """Re-rank chunks by relevance to question.
        
        Args:
            question: user question
            chunks: candidate chunks to re-rank
            top_k: return top-k after re-ranking
        
        Returns: List of (chunk, score) sorted by score descending.
        """
        if not chunks:
            return []
        
        # Pair each chunk with the question
        pairs = [[question, chunk.text] for chunk in chunks]
        
        # Score all pairs
        scores = self.model.predict(pairs)
        
        # Rank by score
        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return ranked[:top_k]
