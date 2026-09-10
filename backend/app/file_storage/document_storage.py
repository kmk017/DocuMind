"""
Local physical file storage helper for DocuMind documents.

Responsibilities (and ONLY these):
    - Determine the storage root directory
    - Ensure the storage directory exists
    - Generate unique stored filenames
    - Resolve stored filenames to safe physical paths
    - Save files to disk
    - Delete files from disk

This module intentionally does NOT:
    - Import or touch the Document SQLAlchemy model
    - Access the database in any way
    - Handle Flask requests or build API responses
    - Validate file size, extension, or MIME type (business validation
      belongs to the future Upload API)
"""

import uuid
from pathlib import Path

# The storage root is calculated relative to this file's location, not the
# current working directory. This file lives at:
#   backend/app/file_storage/document_storage.py
# so walking up three parents lands on `backend/`, and appending
# `storage/documents` gives the final target regardless of where the
# application process was launched from.
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
STORAGE_ROOT = _BACKEND_ROOT / "storage" / "documents"


def ensure_storage_directory() -> Path:
    """Create the document storage directory if it doesn't already exist.

    Safe to call repeatedly (idempotent). Returns the storage root path.
    """
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    return STORAGE_ROOT


def generate_stored_filename(original_filename: str) -> str:
    """Generate a unique, safe filename for physical storage.

    Takes only the extension from the original filename; the rest of the
    original name is discarded and never used on disk. The original
    filename should be persisted separately as metadata (in the database),
    not derived from the stored filename.

    Example:
        "resume.pdf" -> "550e8400-e29b-41d4-a716-446655440000.pdf"
    """
    extension = Path(original_filename).suffix  # includes the leading dot, e.g. ".pdf"
    return f"{uuid.uuid4()}{extension}"


def resolve_path(stored_filename: str) -> Path:
    """Resolve a stored filename to its full physical path, guaranteeing
    the result stays inside the storage root.

    Raises:
        ValueError: if the resolved path would escape the storage root
            (e.g. a stored_filename containing path-traversal segments).
    """
    ensure_storage_directory()

    candidate = (STORAGE_ROOT / stored_filename).resolve()
    storage_root_resolved = STORAGE_ROOT.resolve()

    if not candidate.is_relative_to(storage_root_resolved):
        raise ValueError(
            "Resolved path escapes the storage directory; refusing to proceed."
        )

    return candidate


def save_file(file_obj, stored_filename: str) -> Path:
    """Save a file-like object to disk under the given stored filename.

    Args:
        file_obj: a file-like object supporting .save(path) (e.g. Werkzeug's
            FileStorage) OR a plain binary file object supporting .read().
        stored_filename: the UUID-based filename to save under (see
            generate_stored_filename).

    Returns:
        The full physical Path the file was saved to.

    Raises:
        ValueError: if the target path would escape the storage root, or
            if a file already exists at that path (refuses to overwrite).
    """
    target_path = resolve_path(stored_filename)

    if target_path.exists():
        raise ValueError(
            f"Refusing to overwrite existing file: {target_path.name}"
        )

    if hasattr(file_obj, "save"):
        # Werkzeug FileStorage-style object (what Flask will hand us later).
        file_obj.save(str(target_path))
    else:
        # Generic binary file-like object.
        with open(target_path, "wb") as f:
            f.write(file_obj.read())

    return target_path


def delete_file(stored_filename: str) -> bool:
    """Delete a stored document file.

    Returns:
        True if a file was deleted, False if there was nothing to delete
        (already missing/deleted) — this is treated as a success case, not
        an error.

    Raises:
        ValueError: if the resolved path would escape the storage root.
        OSError: if a real filesystem failure occurs (e.g. permissions);
            this is intentionally allowed to propagate to the caller.
    """
    target_path = resolve_path(stored_filename)

    if not target_path.exists():
        return False

    target_path.unlink()
    return True