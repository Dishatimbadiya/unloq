"""BM25 keyword search fallback for low embedding similarity.

BM25 is a proven keyword-based retrieval method. When embedding-based retrieval
scores are low, BM25 catches keyword-based queries effectively.
"""
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from ..core import DocumentChunk


class BM25Search:
    """BM25 keyword search index."""
    
    def __init__(self):
        """Initialize BM25 search."""
        self.corpus: List[str] = []
        self.chunks: List[DocumentChunk] = []
        self.bm25: BM25Okapi | None = None
    
    def index(self, chunks: List[DocumentChunk]):
        """Index chunks for BM25 search.
        
        Args:
            chunks: policy chunks to index
        """
        self.chunks = chunks
        self.corpus = [chunk.text for chunk in chunks]
        # Simple tokenization by whitespace
        tokenized_corpus = [text.split() for text in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
    
    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search chunks by keywords using BM25.
        
        Args:
            query: user question or keywords
            top_k: number of results to return
        
        Returns:
            List of (chunk, score) sorted by score descending
        """
        if not self.bm25:
            return []
        
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Rank by score
        ranked = sorted(
            zip(self.chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return ranked[:top_k]
