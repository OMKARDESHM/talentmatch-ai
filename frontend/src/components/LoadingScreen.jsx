export default function LoadingScreen({
  message = "Loading your TalentMatch workspace...",
}) {
  return (
    <main className="loading-screen">
      <div className="loading-card">
        <div className="brand-mark" aria-hidden="true">
          TM
        </div>
        <p>{message}</p>
      </div>
    </main>
  );
}
