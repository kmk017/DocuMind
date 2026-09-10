from datetime import datetime, timezone

from app.extensions import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False,
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
    )

    file_type = db.Column(
        db.String(10),
        nullable=False,
    )

    file_size = db.Column(
        db.Integer,
        nullable=False,
    )

    storage_path = db.Column(
        db.String(500),
        nullable=False,
    )

    upload_timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="uploaded",
    )

    extracted_text = db.Column(
        db.Text,
        nullable=True,
    )

    user = db.relationship(
        "User",
        back_populates="documents",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "upload_timestamp": self.upload_timestamp.isoformat(),
            "status": self.status,
        }

    def __repr__(self):
        return (
            f"<Document id={self.id} "
            f"original_filename={self.original_filename!r}>"
        )