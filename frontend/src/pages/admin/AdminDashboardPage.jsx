import { useAuth } from "../../auth/useAuth";

export default function AdminDashboardPage() {
  const { user } = useAuth();

  return (
    <section className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">ADMIN WORKSPACE</p>
          <h1>Hiring dashboard</h1>
          <p>
            Signed in as {user.email}. Job and application management
            will be connected to the existing API.
          </p>
        </div>
      </header>

      <div className="dashboard-placeholder">
        <span>Company administration</span>
        <h2>Jobs, applicants, and pipeline visibility</h2>
        <p>
          Admin workflows and dashboard analytics will be connected
          in the dedicated admin frontend phase.
        </p>
      </div>
    </section>
  );
}