from .embedding_service import generate_embedding
from .models import DocumentChunk, Document

DEFAULT_LIMIT = 5
DEFAULT_MAX_DISTANCE = 0.80


def search_similar_chunks(
    query,
    user_id,
    document_id=None,
    limit=DEFAULT_LIMIT,
    max_distance=DEFAULT_MAX_DISTANCE,
):
    if not query or not query.strip():
        return []

    if not user_id:
        return []

    query_embedding = generate_embedding(query, input_type="query")

    base_query = (
        DocumentChunk.query
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .filter(
            Document.user_id == user_id,
            DocumentChunk.embedding.isnot(None),
        )
    )

    # If a document is selected, search ONLY that document.
    if document_id is not None:
        base_query = base_query.filter(
            Document.id == document_id
        )

    base_query = (
        base_query
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
    )

    # First try with the relevance threshold.
    results = (
        base_query
        .filter(
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            ) <= max_distance
        )
        .limit(limit)
        .all()
    )

    # Fallback to closest chunks if threshold removes everything.
    if not results:
        results = (
            base_query
            .limit(limit)
            .all()
        )

    return results


def build_context(chunks):
    context_parts = []
    seen_chunks = set()

    for chunk, distance in chunks:
        source_key = (
            chunk.document_id,
            chunk.chunk_index,
        )

        if source_key in seen_chunks:
            continue

        seen_chunks.add(source_key)

        context_parts.append(
            f"[Document {chunk.document_id}, "
            f"Chunk {chunk.chunk_index}]\n"
            f"{chunk.content}"
        )

    return "\n\n".join(context_parts)