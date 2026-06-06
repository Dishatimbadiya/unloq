"""Tests for generation module."""
import pytest
from src.unloq_rag.generation import assemble_prompt, parse_markdown_answer


def test_assemble_prompt(mock_policy_chunks):
    """Test prompt assembly."""
    prompt = assemble_prompt("What's the travel limit?", mock_policy_chunks)
    
    assert "What's the travel limit?" in prompt
    assert "POL-FIN-001" in prompt
    assert "$150/day" in prompt


def test_parse_markdown_answer():
    """Test markdown answer parsing."""
    markdown_answer = """
# Answer

The daily travel limit is $150/day [POL-FIN-001].

# Citations

- POL-FIN-001

# Confidence

HIGH
"""
    result = parse_markdown_answer(markdown_answer)
    
    assert "$150/day" in result.answer
    assert result.confidence == "HIGH"
    assert len(result.citations) == 1
