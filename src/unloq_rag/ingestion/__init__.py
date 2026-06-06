"""Ingestion module: PDF parsing and chunking."""
from .pdf_parser import extract_text_with_pages, extract_full_text
from .chunker import chunk_text

__all__ = ["extract_text_with_pages", "extract_full_text", "chunk_text"]
