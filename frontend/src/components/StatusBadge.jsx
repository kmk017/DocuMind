import "./StatusBadge.css";

const STATUS_LABELS = {
  uploaded: "Uploaded",
  processing: "Processing",
  processed: "Processed",
  failed: "Failed",
};

export default function StatusBadge({ status }) {
  const label = STATUS_LABELS[status] || status || "Unknown";
  const variant = STATUS_LABELS[status] ? status : "unknown";

  return (
    <span className={`status-indicator status-indicator--${variant}`}>
      <span className="status-indicator__dot" aria-hidden="true" />
      {label}
    </span>
  );
}
