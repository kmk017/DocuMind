"""
Temporary manual verification script for the Phase 3.1 PDF extraction
module.

This is NOT an automated test suite — just a straightforward script that
exercises the extractor against a real generated PDF and a couple of edge
cases, so results can be reviewed by eye.

Note: this script uses `reportlab` only to GENERATE a sample PDF to test
against. reportlab is a test-only convenience here, not a project
dependency — it is not added to requirements.txt.

Safe to delete after verification.
Run with:
    python test_pdf_extraction_manual.py
"""

from pathlib import Path

from reportlab.pdfgen import canvas

from app.document_processing.pdf_extractor import (
    PDFExtractionError,
    extract_text_from_pdf,
)

SAMPLE_DIR = Path("test_pdfs")


def make_sample_pdf(path: Path, lines: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path))
    y = 750
    for line in lines:
        c.drawString(72, y, line)
        y -= 20
    c.save()


def main():
    SAMPLE_DIR.mkdir(exist_ok=True)

    print("1. Generating a real multi-page sample PDF with text...")
    sample_path = SAMPLE_DIR / "sample.pdf"
    make_sample_pdf(sample_path, [
        "DocuMind Phase 3.1 Test Document",
        "This is a real PDF generated for extraction testing.",
        "It contains multiple lines of readable text.",
    ])
    print(f"   Created: {sample_path}")

    print("\n2. Extracting text from the sample PDF...")
    text = extract_text_from_pdf(sample_path)
    print("   Extracted text:")
    print("   " + "\n   ".join(text.splitlines()))
    print(f"   Non-empty result: {len(text.strip()) > 0}")

    print("\n3. Attempting extraction on a missing file...")
    try:
        extract_text_from_pdf(SAMPLE_DIR / "does_not_exist.pdf")
        print("   UNEXPECTED: no error was raised!")
    except PDFExtractionError as e:
        print(f"   Correctly raised PDFExtractionError: {e}")

    print("\n4. Attempting extraction on a corrupt/non-PDF file...")
    fake_pdf = SAMPLE_DIR / "not_really_a_pdf.pdf"
    fake_pdf.write_bytes(b"this is not a real pdf file")
    try:
        extract_text_from_pdf(fake_pdf)
        print("   UNEXPECTED: no error was raised!")
    except PDFExtractionError as e:
        print(f"   Correctly raised PDFExtractionError: {e}")

    print("\n5. Extracting from a PDF with a blank (imageless, textless) page...")
    blank_path = SAMPLE_DIR / "blank.pdf"
    c = canvas.Canvas(str(blank_path))
    c.showPage()  # a page with nothing drawn on it
    c.save()
    text = extract_text_from_pdf(blank_path)
    print(f"   Extraction did not crash. Result: {repr(text)}")

    print("\n   Cleaning up generated test PDFs...")
    for f in SAMPLE_DIR.glob("*.pdf"):
        f.unlink()
    SAMPLE_DIR.rmdir()
    print("   Cleanup complete.")

    print("\nAll manual checks complete.")


if __name__ == "__main__":
    main()