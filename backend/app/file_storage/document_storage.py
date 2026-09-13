"""
Supabase Storage helper for DocuMind documents.

Responsibilities:
    - Generate unique stored filenames
    - Upload documents to Supabase Storage
    - Download documents temporarily for processing
    - Delete documents from Supabase Storage

This module does NOT:
    - Access the Document SQLAlchemy model
    - Handle Flask requests
    - Perform PDF/DOCX extraction
    - Perform AI/LLM processing
"""

import os
import tempfile
import uuid
from pathlib import Path

from ..supabase_client import supabase


BUCKET_NAME = os.getenv(
    "SUPABASE_STORAGE_BUCKET",
    "documents",
)


def generate_stored_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving the extension."""

    extension = Path(original_filename).suffix.lower()

    return f"{uuid.uuid4()}{extension}"


def save_file(file_obj, stored_filename: str) -> int:
    """
    Upload a file to Supabase Storage.

    Returns:
        Uploaded file size in bytes.
    """

    if not stored_filename:
        raise ValueError("Stored filename is required.")

    if hasattr(file_obj, "read"):
        file_obj.seek(0)
        file_data = file_obj.read()
    else:
        raise ValueError("File object must support read().")

    if not file_data:
        raise ValueError("Cannot upload an empty file.")

    supabase.storage.from_(BUCKET_NAME).upload(
        path=stored_filename,
        file=file_data,
        file_options={
            "upsert": "false",
        },
    )

    return len(file_data)


def download_file(stored_filename: str) -> Path:
    """
    Download a document from Supabase Storage into a temporary file.

    The returned file is intended only for document processing.
    """

    if not stored_filename:
        raise ValueError("Stored filename is required.")

    file_data = supabase.storage.from_(BUCKET_NAME).download(
        stored_filename
    )

    suffix = Path(stored_filename).suffix

    temporary_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    )

    try:
        temporary_file.write(file_data)
        temporary_file.flush()
        return Path(temporary_file.name)
    finally:
        temporary_file.close()


def delete_file(stored_filename: str) -> bool:
    """
    Delete a document from Supabase Storage.

    Returns:
        True when the delete request succeeds.
    """

    if not stored_filename:
        return False

    supabase.storage.from_(BUCKET_NAME).remove(
        [stored_filename]
    )

    return True