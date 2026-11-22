"""
Utility modules for SmartSOP AI:
- pdf_parser: Industrial PDF extraction with table-to-Markdown and heading detection.
- chunker: Table-aware semantic chunking for factory SOP documents.
"""

from app.utils.pdf_parser import (
    extract_text_by_page,
    extract_tables_as_markdown,
    detect_headings,
    parse_pdf_document,
)
from app.utils.chunker import (
    chunk_document,
    TableAwareChunker,
)

__all__ = [
    "extract_text_by_page",
    "extract_tables_as_markdown",
    "detect_headings",
    "parse_pdf_document",
    "chunk_document",
    "TableAwareChunker",
]

