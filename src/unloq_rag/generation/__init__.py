"""Generation module: prompt assembly and LLM integration."""
from .generator import assemble_prompt, call_llm, generate_answer, parse_markdown_answer

__all__ = [
    "assemble_prompt",
    "call_llm",
    "generate_answer",
    "parse_markdown_answer",
]
