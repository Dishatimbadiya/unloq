"""Embedding service using BAAI/bge-large-en-v1.5.

High-quality, open-source embeddings with dimension 1024.
Competitive with commercial offerings and very efficient.
"""
from typing import List
from sentence_transformers import SentenceTransformer
from ..core import EmbeddingError


class EmbeddingService:
    """Embed text using sentence-transformers."""
    
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        """Initialize embedding model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise EmbeddingError(f"Failed to load embedding model: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text.
        
        Args:
            text: text to embed
        
        Returns:
            Embedding vector as list of floats
        """
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            raise EmbeddingError(f"Embedding failed: {e}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts efficiently (batch).
        
        Args:
            texts: list of texts to embed
        
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return [e.tolist() for e in embeddings]
        except Exception as e:
            raise EmbeddingError(f"Batch embedding failed: {e}")
