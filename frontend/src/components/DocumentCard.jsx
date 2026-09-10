import { useState } from "react";
import { deleteDocument } from "../services/api";
import StatusBadge from "./StatusBadge";
import "./DocumentCard.css";

function formatFileSize(bytes) {
  if (typeof bytes !== "number" || Number.isNaN(bytes)) return null;

  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(isoString) {
  if (!isoString) return null;

  const date = new Date(isoString);

  if (Number.isNaN(date.getTime())) return null;

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function DocumentCard({ document, onDeleted, onOpen }) {
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const fileSizeLabel = formatFileSize(document.file_size);
  const uploadDateLabel = formatDate(document.upload_timestamp);
  const typeLabel = (document.file_type || "").toUpperCase() || "FILE";

  const handleDelete = async () => {
    setIsDeleting(true);
    setDeleteError("");

    try {
      await deleteDocument(document.id);

      onDeleted?.(document.id);
    } catch (err) {
      setDeleteError(err.message || "Could not delete this document.");
      setIsDeleting(false);
      setIsConfirmingDelete(false);
    }
  };

  return (
    <li className="document-card">
      <div className="document-card__head">
        <span
          className={`document-card__type document-card__type--${document.file_type}`}
        >
          {typeLabel}
        </span>

        <StatusBadge status={document.status} />
      </div>

      <p
        className="document-card__name"
        title={document.original_filename}
      >
        {document.original_filename}
      </p>

      <p className="document-card__meta">
        {fileSizeLabel && <span>{fileSizeLabel}</span>}

        {fileSizeLabel && uploadDateLabel && (
          <span aria-hidden="true"> · </span>
        )}

        {uploadDateLabel && (
          <span>Uploaded {uploadDateLabel}</span>
        )}
      </p>

      <div className="document-card__actions">
        <button
          type="button"
          className="document-card__action"
          onClick={() => onOpen?.(document)}
        >
          Open
        </button>

        {!isConfirmingDelete ? (
          <button
            type="button"
            className="document-card__action document-card__action--danger"
            onClick={() => setIsConfirmingDelete(true)}
          >
            Delete
          </button>
        ) : (
          <span className="document-card__confirm">
            <span className="document-card__confirm-text">
              Delete?
            </span>

            <button
              type="button"
              className="document-card__action document-card__action--danger"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? "Deleting…" : "Yes"}
            </button>

            <button
              type="button"
              className="document-card__action"
              onClick={() => setIsConfirmingDelete(false)}
              disabled={isDeleting}
            >
              Cancel
            </button>
          </span>
        )}
      </div>

      {deleteError && (
        <p className="document-card__error">
          {deleteError}
        </p>
      )}
    </li>
  );
}