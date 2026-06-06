"""Core data types and models."""
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class DocumentChunk:
    """A chunk of a policy document with metadata."""
    policy_id: str
    source: str
    page: Optional[int]
    chunk_id: str
    text: str
    embedding: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    """Result from vector/BM25 retrieval."""
    chunks: List[DocumentChunk]
    scores: List[float]


@dataclass
class AnswerResult:
    """Final structured answer."""
    answer: str
    citations: List[Dict]
    conflict: Optional[Dict]
    confidence: str  # HIGH | MEDIUM | LOW
    answer_trace: Optional[str]
