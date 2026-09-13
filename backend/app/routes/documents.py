from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from ..auth.decorators import token_required
from ..document_service import (
    DocumentServiceError,
    process_and_store_document,
)
from ..search_service import search_similar_chunks, build_context
from ..llm_service import generate_answer
from ..extensions import db
from ..file_storage import document_storage as storage
from ..models import Document, DocumentChunk


documents_bp = Blueprint("documents", __name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _error(message: str, status_code: int):
    return jsonify({"error": message}), status_code


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@documents_bp.route("/api/documents", methods=["POST"])
@token_required
def upload_document():

    # ---- 1. Validate request ----

    if "file" not in request.files:
        return _error("No file was provided.", 400)

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return _error("No file was selected.", 400)

    original_filename = uploaded_file.filename
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return _error(
            "Only PDF and DOCX files are supported.",
            400,
        )

    # ---- 2. Generate stored filename ----

    stored_filename = storage.generate_stored_filename(
        original_filename
    )
    
    try:
        file_size = storage.save_file(
            uploaded_file,
            stored_filename,
        )
    
    except Exception:
        current_app.logger.exception(
            "Failed to save uploaded file to Supabase Storage."
        )
    
        return _error(
            "Could not save the file. Please try again.",
            500,
        )

    # ---- 4. Create database record ----

    try:
        document = Document(
            user_id=request.user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type=extension.lstrip("."),
            file_size=file_size,
            storage_path=stored_filename,
        )

        db.session.add(document)
        db.session.commit()

    except Exception:
        db.session.rollback()

        try:
            storage.delete_file(stored_filename)
        except Exception:
            current_app.logger.exception(
                "Failed to clean up orphaned Supabase Storage object "
                "after database error."
            )

        current_app.logger.exception(
            "Failed to create document record."
        )

        return _error(
            "A database error occurred. Please try again.",
            500,
        )

    # ---- 5. Process document ----

    try:
        document = process_and_store_document(document)

    except DocumentServiceError:

        current_app.logger.error(
            "Document id=%s was uploaded successfully "
            "but processing failed.",
            document.id,
        )

        return _error(
            "Document uploaded, but processing failed.",
            500,
        )

    # ---- 6. Return document ----

    return jsonify(document.to_dict()), 201


# ============================================================
# LIST USER DOCUMENTS
# ============================================================

@documents_bp.route("/api/documents", methods=["GET"])
@token_required
def list_documents():

    try:
        documents = (
            Document.query
            .filter_by(user_id=request.user_id)
            .order_by(
                Document.upload_timestamp.desc()
            )
            .all()
        )

    except Exception:

        current_app.logger.exception(
            "Failed to retrieve documents "
            "for user id=%s.",
            request.user_id,
        )

        return _error(
            "Could not retrieve documents.",
            500,
        )

    return jsonify(
        [document.to_dict() for document in documents]
    ), 200


# ============================================================
# GET SINGLE DOCUMENT
# ============================================================

@documents_bp.route(
    "/api/documents/<int:document_id>",
    methods=["GET"],
)
@token_required
def get_document(document_id):

    try:
        document = (
            Document.query
            .filter_by(
                id=document_id,
                user_id=request.user_id,
            )
            .first()
        )

    except Exception:

        current_app.logger.exception(
            "Failed to retrieve document id=%s "
            "for user id=%s.",
            document_id,
            request.user_id,
        )

        return _error(
            "Could not retrieve document.",
            500,
        )

    if document is None:
        return _error(
            "Document not found.",
            404,
        )

    return jsonify(
        document.to_dict()
    ), 200


# ============================================================
# DELETE DOCUMENT
# ============================================================

@documents_bp.route(
    "/api/documents/<int:document_id>",
    methods=["DELETE"],
)
@token_required
def delete_document(document_id):

    # ---- 1. Find document belonging to current user ----

    try:
        document = (
            Document.query
            .filter_by(
                id=document_id,
                user_id=request.user_id,
            )
            .first()
        )

    except Exception:

        current_app.logger.exception(
            "Failed to look up document id=%s "
            "for deletion.",
            document_id,
        )

        return _error(
            "Could not delete document.",
            500,
        )

    if document is None:
        return _error(
            "Document not found.",
            404,
        )

    stored_filename = document.stored_filename

    # ---- 2. Delete chunks and document record ----

    try:

        DocumentChunk.query.filter_by(
            document_id=document_id
        ).delete(
            synchronize_session=False
        )

        db.session.delete(document)
        db.session.commit()

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Failed to delete document and chunks "
            "for document id=%s.",
            document_id,
        )

        return _error(
            "Could not delete document.",
            500,
        )

    # ---- 3. Delete physical file ----

    try:

        file_was_deleted = storage.delete_file(
            stored_filename
        )

        if not file_was_deleted:

            current_app.logger.warning(
                "Supabase Storage object already missing "
                "for document id=%s "
                "(stored_filename=%s).",
                document_id,
                stored_filename,
            )

    except Exception:

        current_app.logger.exception(
            "Document id=%s was deleted from the "
            "database, but the supabase storage object "
            "could not be deleted.",
            document_id,
        )

    return "", 204


# ============================================================
# DOCUMENT STATUS
# ============================================================

@documents_bp.route(
    "/api/documents/<int:document_id>/status",
    methods=["GET"],
)
@token_required
def get_document_status(document_id):

    try:

        document = (
            Document.query
            .filter_by(
                id=document_id,
                user_id=request.user_id,
            )
            .first()
        )

    except Exception:

        current_app.logger.exception(
            "Failed to retrieve document status "
            "for document id=%s.",
            document_id,
        )

        return _error(
            "Could not retrieve document status.",
            500,
        )

    if document is None:
        return _error(
            "Document not found.",
            404,
        )

    return jsonify({
        "id": document.id,
        "status": document.status,
    }), 200


# ============================================================
# VECTOR SEARCH
# ============================================================

@documents_bp.route(
    "/search",
    methods=["POST"],
)
@token_required
def search_documents():

    data = request.get_json(silent=True)

    if not data:
        return _error(
            "Request body is required.",
            400,
        )

    query = data.get("query")

    if not query or not query.strip():
        return _error(
            "Query is required.",
            400,
        )

    # Selected document ID from frontend
    document_id = data.get("document_id")

    if document_id is None:
        return _error(
            "Document ID is required.",
            400,
        )

    try:

        chunks = search_similar_chunks(
            query,
            user_id=request.user_id,
            document_id=document_id,
        )

        results = []

        for chunk, distance in chunks:

            results.append({
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "distance": float(distance),
            })

        return jsonify({
            "query": query,
            "document_id": document_id,
            "results": results,
        }), 200

    except Exception:

        current_app.logger.exception(
            "Document search failed "
            "for user id=%s, document id=%s.",
            request.user_id,
            document_id,
        )

        return _error(
            "Could not search the selected document.",
            500,
        )


# ============================================================
# RAG QUESTION ANSWERING
# ============================================================

@documents_bp.route(
    "/ask",
    methods=["POST"],
)
@token_required
def ask_document():

    data = request.get_json(silent=True)

    if not data:
        return _error(
            "Request body is required.",
            400,
        )

    query = data.get("question")

    if not query or not query.strip():
        return _error(
            "Question is required.",
            400,
        )

    # Selected document ID from frontend
    document_id = data.get("document_id")

    if document_id is None:
        return _error(
            "Document ID is required.",
            400,
        )

    try:

        # ---- 1. Search ONLY inside selected document ----

        chunks = search_similar_chunks(
            query,
            user_id=request.user_id,
            document_id=document_id,
        )

        if not chunks:

            return jsonify({
                "query": query,
                "document_id": document_id,
                "answer": (
                    "I could not find relevant information "
                    "in the selected document."
                ),
                "sources": [],
            }), 200

        # ---- 2. Build context ----

        context = build_context(chunks)

        # ---- 3. Generate answer ----

        answer = generate_answer(
            query,
            context,
        )

        # ---- 4. Build sources ----

        sources = []
        seen_sources = set()

        for chunk, distance in chunks:

            source_key = (
                chunk.document_id,
                chunk.chunk_index,
            )

            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)

            document = db.session.get(
                Document,
                chunk.document_id,
            )

            sources.append({
                "document_id": chunk.document_id,
                "document_name": (
                    document.original_filename
                    if document
                    else "Unknown"
                ),
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "distance": (
                    float(distance)
                    if distance is not None
                    else None
                ),
            })

        # ---- 5. Return RAG response ----

        return jsonify({
            "query": query,
            "document_id": document_id,
            "answer": answer,
            "sources": sources,
        }), 200

    except Exception:

        current_app.logger.exception(
            "RAG question answering failed "
            "for user id=%s, document id=%s.",
            request.user_id,
            document_id,
        )

        return _error(
            "Could not generate an answer.",
            500,
        )