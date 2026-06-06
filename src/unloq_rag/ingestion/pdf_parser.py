"""PDF parsing using PyMuPDF for enterprise PDF support.

Extracts text preserving page structure and metadata.
"""
import fitz
from typing import List, Tuple
from ..core import PDFParseError


def extract_text_with_pages(pdf_path: str) -> List[Tuple[str, int]]:
    """Extract text from PDF with page numbers.
    
    Args:
        pdf_path: path to PDF file
    
    Returns:
        List of (text, page_number) tuples
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise PDFParseError(f"Failed to open PDF: {e}")
    
    pages = []
    for page_num, page in enumerate(doc, start=1):
        try:
            text = page.get_text()
            if text.strip():
                pages.append((text, page_num))
        except Exception as e:
            # log and skip problematic pages
            continue
    
    doc.close()
    return pages


def extract_full_text(pdf_path: str) -> str:
    """Extract full text from PDF, preserving page breaks."""
    pages = extract_text_with_pages(pdf_path)
    return "\n\n---PAGE BREAK---\n\n".join([text for text, _ in pages])
