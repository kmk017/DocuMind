from app import create_app
from app.models import Document, DocumentChunk
from app.embedding_service import generate_embedding

app = create_app()

with app.app_context():

    query = "projects"
    query_embedding = generate_embedding(query)

    results = (
        DocumentChunk.query
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .filter(
            Document.user_id == 2,
            DocumentChunk.embedding.isnot(None),
        )
        .add_columns(
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            ).label("distance")
        )
        .order_by(
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(10)
        .all()
    )

    print(f"\nQUERY: {query}")
    print(f"RESULTS: {len(results)}")

    for chunk, distance in results:
        print(
            f"\nDocument: {chunk.document_id}"
            f"\nChunk: {chunk.chunk_index}"
            f"\nDistance: {distance}"
            f"\nText: {chunk.content[:300]}"
        )