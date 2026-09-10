"""
Document processing persistence service for DocuMind.

Responsibilities (and ONLY these):
    - Call process_document() to extract a Document's text
    - Save the extracted text and updated status to the database
    - Roll back safely on any database failure
    - Translate extraction/database failures into one clean,
      application-level error type

This module intentionally does NOT:
    - Contain any Flask route logic
    - Duplicate any PDF/DOCX/orchestration logic — extraction itself is
      entirely delegated to document_processing.process_document()
    - Delete or otherwise touch the physical file on disk
    - Perform OCR or any AI/LLM processing

Callers (future routes) are responsible for translating
DocumentServiceError into an appropriate HTTP response — this module
never returns or raises anything Flask-specific.
"""

import logging

from .document_processing.document_processor import (
    DocumentProcessingError,
    process_document,
)
from .extensions import db
from .document_processing.chunker import chunk_text
from .models import DocumentChunk
from .embedding_service import generate_embedding

logger = logging.getLogger(__name__)


class DocumentServiceError(Exception):
    """Raised when a document cannot be processed and persisted, for any
    reason — extraction failure or database failure.

    Carries only a short, generic message safe to surface to a caller —
    it deliberately does not include file paths, SQL details, or the
    underlying exception's raw text.
    """


def process_and_store_document(document):
    """Extract a Document's text and persist the result.

    On success: sets document.extracted_text to the extracted text,
    sets document.status to "processed", commits, and returns the
    document.

    On extraction failure: does NOT set extracted_text (no partial
    text is ever saved), best-effort marks document.status as "failed"
    and commits that alone, then raises DocumentServiceError. The
    physical file is never touched or deleted.

    On database failure (either the failure-status commit or the
    success commit): rolls back the session and raises
    DocumentServiceError. The physical file is never touched or
    deleted.

    Args:
        document: an existing Document model instance (already
            persisted, i.e. it has a primary key).

    Returns:
        The same Document instance, updated and committed.

    Raises:
        DocumentServiceError: if extraction or persistence fails for
            any reason. The real exception detail is always logged
            server-side first.
    """
    document_id = document.id

    try:
        extracted_text = process_document(document)
    except DocumentProcessingError as e:
        logger.error(
            "Text extraction failed for document id=%s: %s", document_id, e
        )
        _mark_failed(document)
        raise DocumentServiceError("The document could not be processed.")
    except Exception:
        logger.exception(
            "Unexpected error while extracting text for document id=%s.",
            document_id,
        )
        _mark_failed(document)
        raise DocumentServiceError("The document could not be processed.")

    try:
        chunks = chunk_text(extracted_text)
    
        document.extracted_text = extracted_text
        document.status = "processed"

        DocumentChunk.query.filter_by(
            document_id=document.id
        ).delete()
    
        for index, content in enumerate(chunks):
            embedding = generate_embedding(content)
        
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=content,
                embedding=embedding,
            )
        
            db.session.add(chunk)
    
        db.session.commit()
    
    except Exception:
        db.session.rollback()
        logger.exception(
            "Failed to save processed document id=%s.",
            document_id,
        )
        raise DocumentServiceError("The document could not be processed.")
    return document


def _mark_failed(document):
    """Best-effort: record that processing failed by setting status to
    "failed" and committing just that change.

    This never raises — if this secondary commit itself fails, it's
    logged and swallowed, so it doesn't mask the original extraction
    error the caller is already about to raise.
    """
    try:
        document.status = "failed"
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception(
            "Failed to mark document id=%s as failed after an extraction error.",
            document.id,
        )