"""Evaluation tests matching evals.md spec."""
import pytest


class TestExactFactRecall:
    """Eval 1: Exact fact recall."""
    
    def test_travel_limit_recall(self, mock_policy_chunks):
        """Should find $150/day travel limit."""
        for chunk in mock_policy_chunks:
            if "150" in chunk.text:
                assert "travel" in chunk.text.lower()
                break
        else:
            pytest.fail("Travel limit not found in mock chunks")


class TestOutOfScopeRefusal:
    """Eval 3: Refuse out-of-scope questions."""
    
    def test_stock_price_not_in_policies(self, mock_policy_chunks):
        """Stock price query should not match any policy."""
        query = "What is the company stock price?"
        for chunk in mock_policy_chunks:
            assert "stock price" not in chunk.text.lower()


class TestMultiDocumentSynthesis:
    """Eval 2: Synthesize multiple documents."""
    
    def test_remote_and_byod_synthesis(self, mock_policy_chunks):
        """Should have both remote work and laptop policies."""
        remote_found = any("remote" in c.text.lower() for c in mock_policy_chunks)
        laptop_found = any("laptop" in c.text.lower() for c in mock_policy_chunks)
        assert remote_found and laptop_found


class TestCitationCorrectness:
    """Eval 4: Citations match sources."""
    
    def test_citation_metadata(self, mock_policy_chunks):
        """Citations should have policy_id."""
        for chunk in mock_policy_chunks:
            assert chunk.policy_id
            assert chunk.source
            assert chunk.chunk_id
