export default function SessionRecoveryScreen({
  message,
  isRetrying,
  onRetry,
  onSignOut,
}) {
  return (
    <main className="session-recovery-screen">
      <section className="session-recovery-card">
        <div className="brand-mark" aria-hidden="true">
          TM
        </div>

        <div>
          <p className="eyebrow">SESSION RECOVERY</p>
          <h1>We could not restore your workspace</h1>
          <p className="session-recovery-description">
            {message}
          </p>
        </div>

        <div className="session-recovery-actions">
          <button
            className="primary-button"
            type="button"
            onClick={onRetry}
            disabled={isRetrying}
          >
            {isRetrying ? "Retrying..." : "Retry connection"}
          </button>

          <button
            className="secondary-button"
            type="button"
            onClick={onSignOut}
            disabled={isRetrying}
          >
            Sign out
          </button>
        </div>
      </section>
    </main>
  );
}
