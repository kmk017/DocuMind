"""
Document processing orchestration for DocuMind.

Documents are stored in Supabase Storage.

For processing:
    1. Download the document temporarily.
    2. Run the existing PDF/DOCX extractor.
    3. Delete the temporary local file.
    4. Return extracted text.
"""

import logging

from ..file_storage import document_storage as storage

from .docx_extractor import (
    DOCXExtractionError,
    extract_text_from_docx,
)

from .pdf_extractor import (
    PDFExtractionError,
    extract_text_from_pdf,
)


logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Raised when document text extraction fails."""


def process_document(document) -> str:
    """
    Download a document from Supabase Storage and extract its text.
    """

    file_type = getattr(document, "file_type", None)
    stored_filename = getattr(document, "storage_path", None)
    document_id = getattr(document, "id", None)

    temporary_path = None

    try:

        if file_type not in {"pdf", "docx"}:
            logger.error(
                "Cannot process document id=%s: "
                "unsupported file_type '%s'.",
                document_id,
                file_type,
            )

            raise DocumentProcessingError(
                "This document type is not supported."
            )

        # Download from Supabase Storage.
        temporary_path = storage.download_file(
            stored_filename
        )

        # Extract using the existing extractors.
        if file_type == "pdf":
            return extract_text_from_pdf(
                str(temporary_path)
            )

        return extract_text_from_docx(
            str(temporary_path)
        )

    except (
        PDFExtractionError,
        DOCXExtractionError,
    ) as e:

        logger.error(
            "Text extraction failed for document id=%s "
            "(file_type=%s): %s",
            document_id,
            file_type,
            e,
        )

        raise DocumentProcessingError(
            "The document could not be processed."
        )

    except DocumentProcessingError:
        raise

    except Exception:

        logger.exception(
            "Unexpected error while processing document "
            "id=%s (file_type=%s).",
            document_id,
            file_type,
        )

        raise DocumentProcessingError(
            "The document could not be processed."
        )

    finally:

        # Always remove the temporary local copy.
        if temporary_path is not None:

            try:
                temporary_path.unlink(
                    missing_ok=True
                )

            except Exception:

                logger.warning(
                    "Failed to remove temporary processing "
                    "file for document id=%s.",
                    document_id,
                    exc_info=True,
                )