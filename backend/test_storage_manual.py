"""
Temporary manual verification script for the Phase 2.2 storage helper.

This is NOT an automated test suite (no pytest, no assertions framework) —
just a straightforward script that exercises each storage helper function
and prints what happened, so it can be reviewed by eye.

Safe to delete after verification, or keep around for future manual checks.
Run with:
    python test_storage_manual.py
"""

import io

from app.file_storage import document_storage as storage


def main():
    print("1. Ensuring storage directory exists...")
    storage_dir = storage.ensure_storage_directory()
    print(f"   Storage directory: {storage_dir}")
    print(f"   Exists: {storage_dir.exists()}")

    print("\n2. Generating stored filenames from 'resume.pdf'...")
    name_a = storage.generate_stored_filename("resume.pdf")
    name_b = storage.generate_stored_filename("resume.pdf")
    print(f"   First:  {name_a}")
    print(f"   Second: {name_b}")
    print(f"   Different UUIDs: {name_a != name_b}")
    print(f"   Extension preserved: {name_a.endswith('.pdf')}")
    print(f"   Original name not reused: {'resume' not in name_a}")

    print("\n3. Saving a fake PDF file...")
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content for testing")
    saved_path = storage.save_file(fake_pdf, name_a)
    print(f"   Saved to: {saved_path}")
    print(f"   File exists on disk: {saved_path.exists()}")
    print(f"   File is inside storage root: {saved_path.is_relative_to(storage_dir.resolve())}")

    print("\n4. Attempting to overwrite the same stored filename (should fail)...")
    try:
        storage.save_file(io.BytesIO(b"other content"), name_a)
        print("   UNEXPECTED: overwrite was allowed!")
    except ValueError as e:
        print(f"   Correctly rejected: {e}")

    print("\n5. Resolving path for an existing stored filename...")
    resolved = storage.resolve_path(name_a)
    print(f"   Resolved path: {resolved}")
    print(f"   Matches saved path: {resolved == saved_path}")

    print("\n6. Attempting a path-traversal stored filename (should be rejected)...")
    try:
        storage.resolve_path("../../etc/passwd")
        print("   UNEXPECTED: traversal path was allowed!")
    except ValueError as e:
        print(f"   Correctly rejected: {e}")

    print("\n7. Deleting the saved file...")
    deleted = storage.delete_file(name_a)
    print(f"   Deleted: {deleted}")
    print(f"   File still exists: {saved_path.exists()}")

    print("\n8. Deleting an already-missing file (should not raise)...")
    deleted_again = storage.delete_file(name_a)
    print(f"   Delete returned: {deleted_again} (expected False, no exception)")

    print("\n9. Saving a fake DOCX file for completeness...")
    docx_name = storage.generate_stored_filename("contract.docx")
    fake_docx = io.BytesIO(b"fake docx binary content")
    docx_path = storage.save_file(fake_docx, docx_name)
    print(f"   Saved to: {docx_path}")
    print(f"   Extension preserved: {docx_name.endswith('.docx')}")

    print("\n   Cleaning up test DOCX file...")
    storage.delete_file(docx_name)
    print(f"   Cleaned up: {not docx_path.exists()}")

    print("\nAll manual checks complete.")


if __name__ == "__main__":
    main()