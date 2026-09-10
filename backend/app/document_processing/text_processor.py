"""
Text processing utilities for DocuMind.

Responsibilities:
    - Extract text from a document.
    - Split extracted text into chunks.

This module does NOT:
    - Modify the database
    - Modify the Document model
    - Perform AI/LLM processing
    - Create embeddings
"""


from .chunker import chunk_text
from .document_processor import process_document


def extract_and_chunk_document(document) -> list[str]:
    """Extract a document's text and split it into chunks."""

    extracted_text = process_document(document)

    return chunk_text(extracted_text)