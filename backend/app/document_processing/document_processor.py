"""
Document processing orchestration for DocuMind.

Responsibilities (and ONLY these):
    - Look at a Document's file_type
    - Call the matching extractor (pdf_extractor or docx_extractor) with
      the Document's storage_path
    - Return the extracted text
    - Translate extractor-specific errors into one generic, module-level
      error type

This module intentionally does NOT:
    - Contain any Flask route logic
    - Query or touch the database
    - Access document_storage.py directly
    - Duplicate any PDF/DOCX parsing logic — all real extraction work is
      delegated entirely to pdf_extractor.py / docx_extractor.py
    - Perform OCR or any AI/LLM processing
    - Store extracted text anywhere, or change a Document's status

Callers (future routes/services) are responsible for translating
DocumentProcessingError into an appropriate HTTP response — this module
never returns or raises anything Flask-specific.
"""

import logging

from .docx_extractor import DOCXExtractionError, extract_text_from_docx
from .pdf_extractor import PDFExtractionError, extract_text_from_pdf

logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Raised when a document's text cannot be extracted for any reason —
    an unsupported file type, an extraction failure, or anything
    unexpected.

    Carries only a short, generic message safe to surface to a caller —
    it deliberately does not include the file path or the underlying
    extractor's raw exception text.
    """


def process_document(document) -> str:
    """Extract text from a Document by dispatching to the correct
    extractor based on its file_type.

    Args:
        document: an object exposing `file_type` and `storage_path`
            attributes (in practice, a Document model instance — but
            this function only relies on those two attributes, and does
            not import or depend on the Document class itself).

    Returns:
        The extracted text, exactly as returned by the underlying
        extractor for that file type.

    Raises:
        DocumentProcessingError: if file_type is unsupported, if the
            underlying extractor fails, or if anything unexpected goes
            wrong. The real exception detail is always logged
            server-side first.
    """
    file_type = getattr(document, "file_type", None)
    storage_path = getattr(document, "storage_path", None)
    document_id = getattr(document, "id", None)

    try:
        if file_type == "pdf":
            return extract_text_from_pdf(storage_path)
        elif file_type == "docx":
            return extract_text_from_docx(storage_path)
        else:
            logger.error(
                "Cannot process document id=%s: unsupported file_type '%s'.",
                document_id,
                file_type,
            )
            raise DocumentProcessingError("This document type is not supported.")

    except (PDFExtractionError, DOCXExtractionError) as e:
        # The extractor already logged its own technical detail; add
        # document-level context here before wrapping it into the
        # module's own generic error type.
        logger.error(
            "Text extraction failed for document id=%s (file_type=%s): %s",
            document_id,
            file_type,
            e,
        )
        raise DocumentProcessingError("The document could not be processed.")
    except DocumentProcessingError:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while processing document id=%s (file_type=%s).",
            document_id,
            file_type,
        )
        raise DocumentProcessingError("The document could not be processed.")