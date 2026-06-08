"""BM25 keyword search fallback for low similarity scores.

BM25 is a keyword-based retrieval method that complements semantic search.
Use it when embedding similarity is low to catch keyword-based queries.
"""
from typing import List, Tuple, Dict
from rank_bm25 import BM25Okapi
from .types import DocumentChunk


class BM25Search:
    def __init__(self):
        self.corpus: List[str] = []
        self.chunks: List[DocumentChunk] = []
        self.bm25: BM25Okapi = None
    
    def index(self, chunks: List[DocumentChunk]):
        """Index chunks for BM25 search."""
        self.chunks = chunks
        self.corpus = [chunk.text for chunk in chunks]
        # Tokenize by whitespace (simple)
        tokenized_corpus = [text.split() for text in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
    
    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search by keywords using BM25.
        
        Returns: List of (chunk, score) sorted by score descending.
        """
        if not self.bm25:
            return []
        
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Pair with chunks and rank
        ranked = sorted(
            zip(self.chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return ranked[:top_k]
