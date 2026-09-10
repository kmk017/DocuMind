from .extensions import db
from .models import DocumentChunk


def save_document_chunks(document, chunks):
    """Save document chunks to the database."""

    try:
        for index, content in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=content,
            )
            db.session.add(chunk)

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise