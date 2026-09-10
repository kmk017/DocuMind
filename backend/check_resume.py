from app import create_app
from app.models import Document, DocumentChunk

app = create_app()

with app.app_context():
    docs = (
        Document.query
        .order_by(Document.id.desc())
        .limit(5)
        .all()
    )

    for doc in docs:
        print(
            f"\nDOCUMENT: {doc.id}"
            f" | user_id: {doc.user_id}"
            f" | name: {doc.original_filename}"
            f" | status: {doc.status}"
        )

        chunks = (
            DocumentChunk.query
            .filter_by(document_id=doc.id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

        print(f"  CHUNKS: {len(chunks)}")

        for chunk in chunks[:3]:
            text = chunk.content[:100].replace("\n", " ")

            print(
                f"  CHUNK: {chunk.chunk_index}"
                f" | embedding: {chunk.embedding is not None}"
                f" | text: {text}"
            )