import { useCallback, useId, useRef, useState } from "react";
import { uploadDocument } from "../services/api";
import "./UploadZone.css";

const ACCEPTED_EXTENSIONS = [".pdf", ".docx"];

function getExtension(filename) {
  const lastDot = filename.lastIndexOf(".");
  if (lastDot === -1) return "";
  return filename.slice(lastDot).toLowerCase();
}

function isAcceptedFile(file) {
  return ACCEPTED_EXTENSIONS.includes(getExtension(file.name));
}

export default function UploadZone({ onUploaded }) {
  const [status, setStatus] = useState("idle");
  const [fileName, setFileName] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isDragActive, setIsDragActive] = useState(false);

  const inputRef = useRef(null);
  const inputId = useId();

  const isBusy = status === "uploading";

  const handleFile = useCallback(
    async (file) => {
      if (!file || isBusy) return;

      if (!isAcceptedFile(file)) {
        setStatus("error");
        setFileName(file.name);
        setErrorMessage("Only PDF and DOCX files are supported.");
        return;
      }

      setStatus("uploading");
      setFileName(file.name);
      setErrorMessage("");

      try {
        const document = await uploadDocument(file);

        setStatus("success");
        onUploaded?.(document);

        setTimeout(() => {
          setStatus("idle");
          setFileName("");
        }, 1800);
      } catch (err) {
        setStatus("error");
        setErrorMessage(
          err.message || "Upload failed. Please try again."
        );
      } finally {
        if (inputRef.current) {
          inputRef.current.value = "";
        }
      }
    },
    [isBusy, onUploaded]
  );

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];
    handleFile(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragActive(false);

    if (isBusy) return;

    const file = event.dataTransfer.files?.[0];
    handleFile(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();

    if (!isBusy) {
      setIsDragActive(true);
    }
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  return (
    <div className="upload-zone-wrap">
      <div className="upload-zone-wrap__header">
        <div>
          <p className="upload-zone-wrap__eyebrow">Add to your library</p>
          <h2>Upload a document</h2>
        </div>
        <p>PDF and DOCX files are supported</p>
      </div>
      <label
        htmlFor={inputId}
        className={`upload-zone upload-zone--${status} ${
          isDragActive ? "upload-zone--drag" : ""
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          ref={inputRef}
          id={inputId}
          type="file"
          accept=".pdf,.docx"
          className="upload-zone__input"
          onChange={handleInputChange}
          disabled={isBusy}
          aria-label="Upload a PDF or DOCX document"
        />

        {status === "uploading" && (
          <>
            <span
              className="upload-zone__ring"
              aria-hidden="true"
            />

            <p className="upload-zone__title">
              Processing document
            </p>

            <p className="upload-zone__filename">
              {fileName}
            </p>

            <p className="upload-zone__hint">
              Extracting and preparing your document…
            </p>
          </>
        )}

        {status === "success" && (
          <>
            <span
              className="upload-zone__check"
              aria-hidden="true"
            >
              ✓
            </span>

            <p className="upload-zone__title">
              Document uploaded successfully
            </p>

            <p className="upload-zone__filename">
              {fileName}
            </p>

            <p className="upload-zone__hint">
              It now appears in your documents.
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <svg
              className="upload-zone__icon upload-zone__icon--error"
              width="30"
              height="30"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M12 8v5M12 16h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>

            <p className="upload-zone__title upload-zone__title--error">
              Upload failed
            </p>

            {fileName && (
              <p className="upload-zone__filename">
                {fileName}
              </p>
            )}

            <p className="upload-zone__hint upload-zone__hint--error">
              {errorMessage}
            </p>

            <p className="upload-zone__hint">
              Click or drop a file to try again.
            </p>
          </>
        )}

        {status === "idle" && (
          <>
            <span className="upload-zone__icon-wrap">
              <svg
                className="upload-zone__icon"
                width="30"
                height="30"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M12 15V4M12 4 7.5 8.5M12 4l4.5 4.5"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                <path
                  d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>

            <p className="upload-zone__title">
              Drop your documents here
            </p>

            <p className="upload-zone__hint">
              or click to browse from your computer
            </p>

            <span className="upload-zone__formats">
              PDF · DOCX
            </span>
          </>
        )}
      </label>
    </div>
  );
}
