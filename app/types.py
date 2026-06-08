from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class DocumentChunk:
    policy_id: str
    source: str
    page: Optional[int]
    chunk_id: str
    text: str
    embedding: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    chunks: List[DocumentChunk]
    scores: List[float]


@dataclass
class AnswerResult:
    answer: str
    citations: List[Dict]
    conflict: Optional[Dict]
    confidence: str
    answer_trace: Optional[str]
