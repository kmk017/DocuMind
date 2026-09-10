import DocumentCard from "./DocumentCard";
import "./DocumentList.css";

function ListSkeleton() {
  return (
    <div className="document-grid" aria-hidden="true">
      {[0, 1, 2].map((i) => (
        <div key={i} className="document-list__skeleton-card">
          <span className="document-list__skeleton-block document-list__skeleton-block--icon" />
          <span className="document-list__skeleton-block document-list__skeleton-block--title" />
          <span className="document-list__skeleton-block document-list__skeleton-block--meta" />
        </div>
      ))}
    </div>
  );
}

export default function DocumentList({
  documents,
  isLoading,
  error,
  onRetry,
  onDeleted,
  onOpen,
}) {
  if (isLoading) {
    return <ListSkeleton />;
  }

  if (error) {
    return (
      <div className="document-list__state">
        <p className="document-list__state-title">
          Couldn't load your documents
        </p>

        <p className="document-list__state-text">
          {error}
        </p>

        <button
          type="button"
          className="document-list__retry"
          onClick={onRetry}
        >
          Try again
        </button>
      </div>
    );
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="document-list__state">
        <p className="document-list__state-title">
          No documents yet
        </p>

        <p className="document-list__state-text">
          Upload your first PDF or DOCX to start asking questions.
        </p>

        <a href="#upload" className="document-list__retry">
          Upload documents
        </a>
      </div>
    );
  }

  return (
    <ul className="document-grid">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          onDeleted={onDeleted}
          onOpen={onOpen}
        />
      ))}
    </ul>
  );
}