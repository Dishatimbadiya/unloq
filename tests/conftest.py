"""Pytest configuration and fixtures."""
import pytest
from src.unloq_rag.core import DocumentChunk


@pytest.fixture
def mock_policy_chunks():
    """Mock policy chunks for testing."""
    return [
        DocumentChunk(
            policy_id="POL-FIN-001",
            source="finance_policy.pdf",
            page=3,
            chunk_id="chunk-1",
            text="Employees may claim up to $150/day for international travel meals and local transportation.",
            embedding=[0.1] * 1024
        ),
        DocumentChunk(
            policy_id="POL-IT-002",
            source="it_security.pdf",
            page=7,
            chunk_id="chunk-2",
            text="Employees may use personal laptops only if the device is enrolled in corporate MDM.",
            embedding=[0.2] * 1024
        ),
        DocumentChunk(
            policy_id="POL-HR-003",
            source="remote_work.pdf",
            page=1,
            chunk_id="chunk-3",
            text="Employees may work remotely up to 3 days per week.",
            embedding=[0.3] * 1024
        ),
    ]


@pytest.fixture
def query_embedding():
    """Mock query embedding for testing."""
    return [0.15] * 1024
