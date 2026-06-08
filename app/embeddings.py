"""Embedding service using BAAI/bge-large-en-v1.5 for high-quality embeddings.

BGE embeddings are open-source, competitive with commercial alternatives, and energy-efficient.
Dimension: 1024
"""
from typing import List
from sentence_transformers import SentenceTransformer
import os


class EmbeddingService:
    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5"
    ):
        """Initialize embedding model."""
        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            raise RuntimeError(f"Embedding failed: {e}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts efficiently (batch)."""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return [e.tolist() for e in embeddings]
        except Exception as e:
            raise RuntimeError(f"Batch embedding failed: {e}")
