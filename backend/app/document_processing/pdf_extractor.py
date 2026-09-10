"""
PDF text extraction for DocuMind.

Responsibilities (and ONLY these):
    - Open a PDF file from a given path
    - Extract text page by page
    - Combine the extracted text into a single string
    - Release the file resource correctly

This module intentionally does NOT:
    - Contain any Flask route logic
    - Query or touch the database
    - Know anything about the Document model
    - Perform OCR, DOCX extraction, or any AI/LLM processing

Callers (future routes/services) are responsible for translating
PDFExtractionError into an appropriate HTTP response — this module never
returns or raises anything Flask-specific.
"""

import logging
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Raised when text cannot be extracted from a PDF.

    Carries only a short, generic message safe to surface to a caller —
    it deliberately does not include the file path or the underlying
    library's raw exception text.
    """


def extract_text_from_pdf(pdf_path) -> str:
    """Extract all readable text from a PDF file.

    Args:
        pdf_path: path to the PDF file (str or pathlib.Path).

    Returns:
        The extracted text of every page, concatenated in page order and
        separated by newlines. Pages with no extractable text (e.g. a
        page that is entirely an image, or a page pypdf simply can't
        parse) contribute an empty string rather than raising — the
        overall extraction still succeeds for the rest of the document.

    Raises:
        PDFExtractionError: if the file doesn't exist, isn't a valid PDF,
            or can't be read for any other reason. The real exception
            detail is always logged server-side first.
    """
    path = Path(pdf_path)

    if not path.exists():
        logger.error("PDF extraction failed: file does not exist at %s", path)
        raise PDFExtractionError("The PDF file could not be found.")

    try:
        with open(path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)

            page_texts = []
            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()
                except Exception:
                    # A single malformed/unusual page should not abort
                    # extraction of the rest of the document.
                    logger.warning(
                        "Could not extract text from page %s of %s; "
                        "continuing with remaining pages.",
                        page_number,
                        path.name,
                        exc_info=True,
                    )
                    text = None

                # extract_text() returns "" or None for pages with no
                # extractable text (e.g. scanned/image-only pages).
                page_texts.append(text or "")

            return "\n".join(page_texts)

    except PdfReadError:
        logger.exception("PDF extraction failed: unreadable/corrupt PDF at %s", path)
        raise PDFExtractionError("The PDF file could not be read.")
    except PDFExtractionError:
        raise
    except Exception:
        logger.exception("PDF extraction failed unexpectedly for %s", path)
        raise PDFExtractionError("The PDF file could not be processed.")