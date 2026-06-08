"""Prompt assembly and generation with markdown output format per guide.

This module constructs the final prompt using the system prompt,
retrieved + re-ranked chunks, and calls an LLM with strict grounding rules.
"""
from typing import List, Dict
from .types import DocumentChunk, AnswerResult
import json
from pathlib import Path


SYSTEM_PROMPT = """You are the company Policy Assistant.

You answer ONLY from the supplied policy context.

RULES

1. Every factual statement must include
   a citation in format [POLICY_ID].

2. If information is not present
   in retrieved context:

   Respond:

   "I could not find this information
   in the available policies."

3. Never invent policy details.

4. If retrieved policies conflict:

   - Explicitly mention the conflict.
   - Cite both policies.
   - Do not decide which is correct.

5. Output format (CRITICAL):

# Answer

<answer with inline [POLICY_ID] citations>

# Citations

- POLICY_ID
- POLICY_ID

# Confidence

HIGH | MEDIUM | LOW
"""


def assemble_prompt(query: str, retrieved: List[DocumentChunk]) -> str:
    """Build the full prompt with context."""
    context_blocks = []
    for c in retrieved:
        source_info = f"[{c.policy_id} — {c.source}, page {c.page}]" if c.page else f"[{c.policy_id} — {c.source}]"
        context_blocks.append(f"{source_info}\n{c.text}")
    
    context_section = "\n\n---\n\n".join(context_blocks)
    
    prompt = f"""{SYSTEM_PROMPT}

CONTEXT (retrieved policies):

{context_section}

USER QUESTION:

{query}

ANSWER:
"""
    return prompt


class LLMError(Exception):
    pass


def call_llm(prompt: str) -> str:
    """Stub LLM call: replace with real client call."""
    raise NotImplementedError("LLM integration required (Claude/OpenAI)")


def parse_markdown_answer(raw_answer: str) -> AnswerResult:
    """Parse markdown answer format into AnswerResult."""
    sections = raw_answer.split("#")
    
    answer = ""
    citations = []
    confidence = "MEDIUM"
    
    for section in sections:
        section = section.strip()
        if section.startswith("Answer"):
            answer = section.replace("Answer", "").strip()
        elif section.startswith("Citations"):
            cit_text = section.replace("Citations", "").strip()
            for line in cit_text.split("\n"):
                line = line.strip()
                if line.startswith("-"):
                    pol_id = line.replace("-", "").strip()
                    citations.append({"policy_id": pol_id})
        elif section.startswith("Confidence"):
            conf_text = section.replace("Confidence", "").strip().upper()
            if "HIGH" in conf_text:
                confidence = "HIGH"
            elif "LOW" in conf_text:
                confidence = "LOW"
            else:
                confidence = "MEDIUM"
    
    return AnswerResult(
        answer=answer,
        citations=citations,
        conflict=None,
        confidence=confidence,
        answer_trace=None
    )


def generate_answer(query: str, retrieved: List[DocumentChunk]) -> AnswerResult:
    """Generate answer from retrieved chunks."""
    prompt = assemble_prompt(query, retrieved)
    try:
        raw_answer = call_llm(prompt)
    except NotImplementedError:
        # Fallback stub
        citations = [{"policy_id": c.policy_id} for c in retrieved]
        return AnswerResult(
            answer=f"[STUB] Retrieved {len(retrieved)} policy chunks. LLM not configured.",
            citations=citations,
            conflict=None,
            confidence="LOW",
            answer_trace="llm_stub"
        )
    
    return parse_markdown_answer(raw_answer)
