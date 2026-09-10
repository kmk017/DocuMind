"""
DOCX text extraction for DocuMind.

Responsibilities (and ONLY these):
    - Open a DOCX file from a given path
    - Extract paragraph text in document order
    - Combine the extracted text into a single string
    - Release the file resource correctly

This module intentionally does NOT:
    - Contain any Flask route logic
    - Query or touch the database
    - Know anything about the Document model
    - Access document_storage.py
    - Perform OCR, PDF extraction, or any AI/LLM processing

Callers (future routes/services) are responsible for translating
DOCXExtractionError into an appropriate HTTP response — this module never
returns or raises anything Flask-specific.
"""

import logging
from pathlib import Path

import docx
from docx.opc.exceptions import PackageNotFoundError

logger = logging.getLogger(__name__)


class DOCXExtractionError(Exception):
    """Raised when text cannot be extracted from a DOCX file.

    Carries only a short, generic message safe to surface to a caller —
    it deliberately does not include the file path or the underlying
    library's raw exception text.
    """


def extract_text_from_docx(docx_path) -> str:
    """Extract all readable paragraph text from a DOCX file.

    Args:
        docx_path: path to the DOCX file (str or pathlib.Path).

    Returns:
        The extracted text of every non-empty paragraph, in document
        order, joined by newlines. Completely empty paragraphs (often
        used purely for spacing) are skipped.

    Raises:
        DOCXExtractionError: if the file doesn't exist, isn't a valid
            DOCX, or can't be read for any other reason. The real
            exception detail is always logged server-side first.
    """
    path = Path(docx_path)

    if not path.exists():
        logger.error("DOCX extraction failed: file does not exist at %s", path)
        raise DOCXExtractionError("The DOCX file could not be found.")

    try:
        document = docx.Document(str(path))

        paragraph_texts = [
            paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()
        ]

        return "\n".join(paragraph_texts)

    except PackageNotFoundError:
        logger.exception("DOCX extraction failed: unreadable/corrupt DOCX at %s", path)
        raise DOCXExtractionError("The DOCX file could not be read.")
    except DOCXExtractionError:
        raise
    except Exception:
        logger.exception("DOCX extraction failed unexpectedly for %s", path)
        raise DOCXExtractionError("The DOCX file could not be processed.")