from app.extensions import db
from pgvector.sqlalchemy import Vector

class DocumentChunk(db.Model):
    __tablename__ = "document_chunks"

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=False,
    )

    chunk_index = db.Column(db.Integer, nullable=False)

    content = db.Column(db.Text, nullable=False)

    embedding = db.Column(Vector(2048), nullable=True)

    def __repr__(self):
        return (
            f"<DocumentChunk id={self.id} "
            f"document_id={self.document_id} "
            f"chunk_index={self.chunk_index}>"
        )