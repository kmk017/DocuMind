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
        <span className="document-list__state-icon document-list__state-icon--error" aria-hidden="true">!</span>
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
        <span className="document-list__state-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M7 3.75h6.75L18 8v12.25H7a2 2 0 0 1-2-2V5.75a2 2 0 0 1 2-2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
            <path d="M13 3.75V8h5M8.5 12h6.5M8.5 15.5h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </span>
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
