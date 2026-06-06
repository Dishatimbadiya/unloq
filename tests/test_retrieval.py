"""Tests for retrieval module."""
import pytest
from src.unloq_rag.retrieval import BM25Search


def test_bm25_search(mock_policy_chunks):
    """Test BM25 keyword search."""
    bm25 = BM25Search()
    bm25.index(mock_policy_chunks)
    
    # Search for travel-related query
    results = bm25.search("travel expenses limit", top_k=2)
    assert len(results) <= 2
    assert results[0][0].policy_id == "POL-FIN-001"  # Travel policy should rank first


def test_bm25_empty():
    """Test BM25 with no indexed chunks."""
    bm25 = BM25Search()
    results = bm25.search("test query", top_k=5)
    assert results == []
