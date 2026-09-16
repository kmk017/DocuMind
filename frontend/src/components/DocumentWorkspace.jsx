import { useState } from "react";
import { askQuestion } from "../services/api";
import "./DocumentWorkspace.css";

function DocumentWorkspace({ document, onBack }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedMessages, setExpandedMessages] = useState({});

  const handleAsk = async (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    if (!document?.id) {
      setError("No document is selected.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await askQuestion(
        trimmedQuestion,
        document.id
      );

      const messageId = Date.now();

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          id: messageId,
          question: trimmedQuestion,
          answer: data.answer || "",
          sources: data.sources || [],
        },
      ]);

      setExpandedMessages((previous) => ({
        ...previous,
        [messageId]: true,
      }));

      setQuestion("");
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong while asking the question."
      );
    } finally {
      setLoading(false);
    }
  };

  const toggleMessage = (messageId) => {
    setExpandedMessages((previous) => ({
      ...previous,
      [messageId]: !previous[messageId],
    }));
  };

  const clearConversation = () => {
    setMessages([]);
    setExpandedMessages({});
  };

  return (
    <main className="workspace-page">
      <div className="workspace-header">
        <button
          type="button"
          className="workspace-back-button"
          onClick={onBack}
        >
          <span aria-hidden="true">←</span>
          Back to documents
        </button>

        <div className="workspace-title-block">
          <p className="workspace-eyebrow">
            DOCUMIND AI
          </p>

          <div className="workspace-document-label">
            <span
              className={`workspace-file-type workspace-file-type--${
                document?.file_type || "file"
              }`}
            >
              {(document?.file_type || "FILE").toUpperCase()}
            </span>

            <span
              className="workspace-document-name"
              title={document?.original_filename}
            >
              {document?.original_filename || "Selected document"}
            </span>
          </div>

          <h1>Ask your document</h1>

          <p className="workspace-description">
            Ask questions and get answers grounded only
            in the selected document.
          </p>
        </div>
      </div>

      <section className="workspace-content">
        <form
          className="question-form"
          onSubmit={handleAsk}
        >
          <label htmlFor="document-question">
            Ask DocuMind about this document
          </label>

          <div className="question-input-row">
            <textarea
              id="document-question"
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="For example: What are the key decisions in this document?"
              rows={3}
              disabled={loading}
            />

            <button
              type="submit"
              className="ask-button"
              disabled={
                !question.trim() ||
                loading ||
                !document?.id
              }
            >
              {loading ? (
                <>
                  <span
                    className="ask-button__spinner"
                    aria-hidden="true"
                  />
                  Thinking
                </>
              ) : (
                <>
                  Ask
                  <span aria-hidden="true">↗</span>
                </>
              )}
            </button>
          </div>

          <p className="question-form__hint">
            Answers are generated using information from this
            document.
          </p>
        </form>

        {error && (
          <div
            className="workspace-error"
            role="alert"
          >
            <span
              className="workspace-error__icon"
              aria-hidden="true"
            >
              !
            </span>

            <span>{error}</span>
          </div>
        )}

        {messages.length > 0 && (
          <section className="conversation-section">
            <div className="conversation-header">
              <div className="section-heading">
                <span>Conversation</span>

                <span className="source-count">
                  {messages.length}
                </span>
              </div>

              <button
                type="button"
                className="clear-conversation-button"
                onClick={clearConversation}
                disabled={loading}
              >
                Clear conversation
              </button>
            </div>

            <p className="conversation-intro">
              Each answer is grounded in the selected document and includes its retrieved context.
            </p>

            {messages.map((message) => (
              <div
                className="conversation-item"
                key={message.id}
              >
                <div className="conversation-item-header">
                  <div className="user-question">
                    <span className="message-label">
                      You
                    </span>

                    <p>{message.question}</p>
                  </div>

                  <button
                    type="button"
                    className="conversation-toggle"
                    onClick={() =>
                      toggleMessage(message.id)
                    }
                    aria-expanded={
                      !!expandedMessages[message.id]
                    }
                  >
                    {expandedMessages[message.id]
                      ? "Hide answer ↑"
                      : "Show answer ↓"}
                  </button>
                </div>

                {expandedMessages[message.id] && (
                  <>
                    <div className="assistant-answer">
                      <span className="message-label">
                        DocuMind
                      </span>

                      <div className="answer-card">
                        <p>{message.answer}</p>
                      </div>
                    </div>

                    {message.sources.length > 0 && (
                      <div className="sources-section">
                        <div className="sources-heading">
                          <div className="section-heading">
                            <span>Retrieved sources</span>

                            <span className="source-count">
                              {message.sources.length}
                            </span>
                          </div>

                          <span className="sources-note">
                            Relevant document sections
                          </span>
                        </div>

                        <div className="sources-list">
                          {message.sources.map(
                            (source, sourceIndex) => (
                              <article
                                className="source-card"
                                key={`${source.document_id}-${source.chunk_index}-${sourceIndex}`}
                              >
                                <div className="source-card-header">
                                  <div className="source-document-info">
                                    <strong>
                                      {source.document_name ||
                                        `Document ${source.document_id}`}
                                    </strong>

                                    <span>
                                      Chunk{" "}
                                      {source.chunk_index + 1}
                                    </span>
                                  </div>

                                  {source.distance !==
                                    undefined && (
                                    <span className="source-distance">
                                      {Math.max(
                                        0,
                                        Math.round(
                                          (1 -
                                            source.distance) *
                                            100
                                        )
                                      )}
                                      % match
                                    </span>
                                  )}
                                </div>

                                <p>{source.content}</p>
                              </article>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </section>
        )}

        {!loading &&
          messages.length === 0 &&
          !error && (
            <section className="workspace-empty">
              <div
                className="workspace-empty-icon"
                aria-hidden="true"
              >
                ✦
              </div>

              <h2>
                Ask this document anything
              </h2>

              <p>
                DocuMind will search only{" "}
                <strong>
                  {document?.original_filename ||
                    "the selected document"}
                </strong>{" "}
                and use its relevant information to answer
                your question.
              </p>

              <div className="workspace-empty-examples">
                <span>Try asking about</span>
                <div>
                  <span>Projects</span>
                  <span>Education</span>
                  <span>Experience</span>
                </div>
              </div>
            </section>
          )}
      </section>
    </main>
  );
}

export default DocumentWorkspace;
