import { Link } from "react-router-dom";

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
            Signed in as {user.email}. Manage jobs and move
            candidates through the hiring pipeline.
          </p>
        </div>
      </header>

      <div className="dashboard-grid">
        <article className="dashboard-card">
          <span>Job management</span>
          <h2>Create and manage hiring opportunities</h2>
          <p>
            Publish jobs, review active and closed roles, and control
            candidate availability.
          </p>

          <Link
            className="primary-button"
            to="/admin/jobs"
          >
            Manage jobs
          </Link>
        </article>

        <article className="dashboard-card">
          <span>Application pipeline</span>
          <h2>Review candidate profile snapshots</h2>
          <p>
            Open a job to inspect applicants and update candidates to
            shortlisted or rejected.
          </p>

          <Link
            className="secondary-button"
            to="/admin/jobs"
          >
            Review applicants
          </Link>
        </article>
      </div>
    </section>
  );
}
