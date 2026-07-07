export default function EmptyState({
  title,
  description,
  action = null,
}) {
  return (
    <div className="empty-state">
      <div className="empty-state-mark" aria-hidden="true">
        TM
      </div>

      <h2>{title}</h2>
      <p>{description}</p>

      {action ? <div className="empty-state-action">{action}</div> : null}
    </div>
  );
}