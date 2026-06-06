"""Core module: shared types and exceptions."""
from .types import DocumentChunk, RetrievalResult, AnswerResult
from .exceptions import RAGError, PDFParseError, EmbeddingError, RetrievalError, GenerationError, StorageError

__all__ = [
    "DocumentChunk",
    "RetrievalResult",
    "AnswerResult",
    "RAGError",
    "PDFParseError",
    "EmbeddingError",
    "RetrievalError",
    "GenerationError",
    "StorageError",
]
