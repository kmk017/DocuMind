import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Navbar from "./components/Navbar";
import UploadZone from "./components/UploadZone";
import DocumentList from "./components/DocumentList";
import AmbientBackground from "./components/AmbientBackground";
import DocumentWorkspace from "./components/DocumentWorkspace";
import AuthPage from "./components/AuthPage";

import { useAuth } from "./context/AuthContext";
import { getDocuments } from "./services/api";

import "./App.css";

function App() {
  const {
    user,
    authLoading,
  } = useAuth();

  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [showWorkspace, setShowWorkspace] =
    useState(false);

  // Currently selected document
  const [selectedDocument, setSelectedDocument] =
    useState(null);

  const fetchDocuments = useCallback(async () => {
    if (!user) {
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const data = await getDocuments();

      setDocuments(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (err) {
      setError(
        err.message ||
          "Could not load your documents."
      );
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      fetchDocuments();
    } else {
      setDocuments([]);
      setSelectedDocument(null);
      setShowWorkspace(false);
      setIsLoading(false);
    }
  }, [user, fetchDocuments]);

  const handleUploaded = useCallback(
    (newDocument) => {
      setDocuments((previous) => [
        newDocument,
        ...previous,
      ]);
    },
    []
  );

  const handleDeleted = useCallback(
    (deletedId) => {
      setDocuments((previous) =>
        previous.filter(
          (doc) => doc.id !== deletedId
        )
      );

      // If the deleted document was open,
      // return to the document list.
      setSelectedDocument((current) => {
        if (current?.id === deletedId) {
          setShowWorkspace(false);
          return null;
        }

        return current;
      });
    },
    []
  );

  const handleOpenDocument = useCallback(
    (document) => {
      setSelectedDocument(document);
      setShowWorkspace(true);
    },
    []
  );

  const handleBackToDocuments =
    useCallback(() => {
      setShowWorkspace(false);
      setSelectedDocument(null);
    }, []);

  if (authLoading) {
    return (
      <div className="page">
        <AmbientBackground />

        <div className="auth-loading">
          <div className="auth-loading__spinner" />

          <p>
            Loading DocuMind...
          </p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="page">
        <AmbientBackground />

        <AuthPage />
      </div>
    );
  }

  if (showWorkspace && selectedDocument) {
    return (
      <div className="page">
        <AmbientBackground />

        <Navbar inWorkspace={showWorkspace} onNavigateBack={handleBackToDocuments} />

        <DocumentWorkspace
          document={selectedDocument}
          onBack={handleBackToDocuments}
        />
      </div>
    );
  }

  return (
    <div className="page">
      <AmbientBackground />

      <Navbar />

      <main className="page__content">

        <section className="hero">
          <div className="hero__text">

            <p className="hero__eyebrow">
              Document intelligence workspace
            </p>

            <h1 className="hero__heading">
              Turn documents into clear answers.
            </h1>

            <p className="hero__subtitle">
              Upload your files, surface relevant context, and ask
              grounded questions—all in one focused workspace.
            </p>

            <a
              href="#upload"
              className="hero__cta"
            >
              Upload documents
            </a>

            <dl className="hero__highlights" aria-label="DocuMind capabilities">
              <div>
                <dt>01</dt>
                <dd>Upload PDF &amp; DOCX</dd>
              </div>
              <div>
                <dt>02</dt>
                <dd>Ask grounded questions</dd>
              </div>
              <div>
                <dt>03</dt>
                <dd>Review source context</dd>
              </div>
            </dl>

          </div>
        </section>

        <section
          id="upload"
          className="upload-section"
        >
          <UploadZone
            onUploaded={handleUploaded}
          />
        </section>

        <section
          id="documents"
          className="documents-section"
        >
          <div className="documents-section__header">
            <div>
              <p className="section-eyebrow">Knowledge library</p>
              <h2 className="documents-section__heading">
                Your documents
              </h2>
            </div>

            {!isLoading &&
              !error &&
              documents.length > 0 && (
                <span className="documents-section__count">
                  {documents.length}{" "}
                  {documents.length === 1
                    ? "document"
                    : "documents"}
                </span>
              )}

          </div>

          <DocumentList
            documents={documents}
            isLoading={isLoading}
            error={error}
            onRetry={fetchDocuments}
            onDeleted={handleDeleted}
            onOpen={handleOpenDocument}
          />

        </section>

      </main>
    </div>
  );
}

export default App;
