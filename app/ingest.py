"""Ingestion and chunking utilities (stubs).

This module defines the expected functions for PDF ingestion, text extraction,
chunking, and embedding generation. In production, implement PDF parsing (e.g., pdfminer, Tika),
OCR where necessary, and call an embedding service.
"""
from typing import List, Iterable
from .types import DocumentChunk
import uuid


def parse_pdf_to_text(path: str) -> str:
    """Parse a PDF and return plain text. Stubbed for now."""
    raise NotImplementedError("PDF parsing not implemented")


def chunk_text(text: str, policy_id: str, source: str, chunk_size: int = 1000, overlap: int = 200) -> List[DocumentChunk]:
    """Simple text chunker returning DocumentChunk list.

    This implementation is a pure-text demonstrator; production should preserve page numbers and offsets.
    """
    chunks: List[DocumentChunk] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        chunks.append(DocumentChunk(
            policy_id=policy_id,
            source=source,
            page=None,
            chunk_id=f"{policy_id}-{idx}-{uuid.uuid4().hex[:8]}",
            text=chunk_text
        ))
        idx += 1
        start = end - overlap
    return chunks


def embed_chunks(chunks: Iterable[DocumentChunk]) -> List[DocumentChunk]:
    """Call embedding service and attach embeddings to chunks. Stubbed now."""
    # In production: call sentence-transformers or OpenAI embeddings and set chunk.embedding
    for c in chunks:
        c.embedding = None
    raise NotImplementedError("Embedding service integration required")
