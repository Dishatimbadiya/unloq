"""Re-ranker using Cross Encoder for precision improvement.

Cross Encoders directly compare (question, candidate) pairs for better accuracy.
They improve precision by ~20% compared to bi-encoders alone.
"""
from typing import List, Tuple
from sentence_transformers import CrossEncoder
from ..core import DocumentChunk, RetrievalError


class ReRanker:
    """Cross Encoder based re-ranking for precision improvement."""
    
    def __init__(self, model_name: str = "cross-encoder/msl-mcd6"):
        """Initialize Cross Encoder model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        try:
            self.model = CrossEncoder(model_name)
        except Exception as e:
            raise RetrievalError(f"Failed to load reranker model: {e}")
    
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
        
        Returns:
            List of (chunk, score) sorted by score descending
        """
        if not chunks:
            return []
        
        # Pair each chunk with the question for comparison
        pairs = [[question, chunk.text] for chunk in chunks]
        
        # Score all (question, candidate) pairs
        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            raise RetrievalError(f"Re-ranking failed: {e}")
        
        # Rank by score descending
        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return ranked[:top_k]
