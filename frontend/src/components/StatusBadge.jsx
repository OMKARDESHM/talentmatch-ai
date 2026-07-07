function formatStatus(status) {
  if (!status) {
    return "Unknown";
  }

  return status
    .split("_")
    .map(
      (part) =>
        part.charAt(0).toUpperCase() + part.slice(1),
    )
    .join(" ");
}

export default function StatusBadge({ status }) {
  const normalizedStatus = status?.toLowerCase() ?? "unknown";

  return (
    <span
      className={`status-badge status-${normalizedStatus}`}
    >
      {formatStatus(status)}
    </span>
  );
}