import "./LoadingSpinner.css";

export default function LoadingSpinner({ label = "Loading" }) {
  return (
    <span className="loading-spinner" role="status" aria-live="polite">
      <span className="loading-spinner__ring" aria-hidden="true" />
      <span className="loading-spinner__label">{label}</span>
    </span>
  );
}
