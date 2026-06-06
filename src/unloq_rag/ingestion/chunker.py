"""Text chunking utilities for policy documents."""
from typing import List
import uuid
from ..core import DocumentChunk


def chunk_text(
    text: str,
    policy_id: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[DocumentChunk]:
    """Split text into overlapping chunks preserving semantic boundaries.
    
    Args:
        text: raw document text
        policy_id: unique policy identifier
        source: source filename
        chunk_size: target chunk size in characters
        overlap: overlap between consecutive chunks
    
    Returns:
        List of DocumentChunk objects
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
            chunk_id=f"{policy_id}-chunk-{idx}-{uuid.uuid4().hex[:8]}",
            text=chunk_text
        ))
        idx += 1
        start = end - overlap
    
    return chunks if chunks else [
        DocumentChunk(
            policy_id=policy_id,
            source=source,
            page=None,
            chunk_id=f"{policy_id}-full",
            text=text
        )
    ]
