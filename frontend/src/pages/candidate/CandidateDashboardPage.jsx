import { useAuth } from "../../auth/useAuth";

export default function CandidateDashboardPage() {
  const { user } = useAuth();

  return (
    <section className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">CANDIDATE WORKSPACE</p>
          <h1>Candidate dashboard</h1>
          <p>
            Signed in as {user.email}. Your job discovery and
            application workspace is ready.
          </p>
        </div>
      </header>

      <div className="dashboard-placeholder">
        <span>Candidate experience</span>
        <h2>Profile, matching, jobs, and applications</h2>
        <p>
          Candidate workflows will be connected to the existing API
          in the next frontend phase.
        </p>
      </div>
    </section>
  );
}