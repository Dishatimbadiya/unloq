"""Core exceptions for RAG system."""


class RAGError(Exception):
    """Base exception for RAG system."""
    pass


class PDFParseError(RAGError):
    """PDF parsing failed."""
    pass


class EmbeddingError(RAGError):
    """Embedding service error."""
    pass


class RetrievalError(RAGError):
    """Retrieval/search failed."""
    pass


class GenerationError(RAGError):
    """LLM generation failed."""
    pass


class StorageError(RAGError):
    """Database/storage operation failed."""
    pass
