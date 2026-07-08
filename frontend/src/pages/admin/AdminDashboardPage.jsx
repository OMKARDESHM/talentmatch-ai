import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getAdminDashboardAnalytics } from "../../api/analyticsApi";
import { useAuth } from "../../auth/useAuth";
import ErrorMessage from "../../components/ErrorMessage";
import LoadingScreen from "../../components/LoadingScreen";

export default function AdminDashboardPage() {
  const { token, user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadAnalytics() {
      try {
        setError("");

        const data = await getAdminDashboardAnalytics(
          token,
          controller.signal,
        );

        setAnalytics(data);
      } catch (requestError) {
        if (requestError.name === "AbortError") {
          return;
        }

        setError(requestError.message);
      }
    }

    loadAnalytics();

    return () => {
      controller.abort();
    };
  }, [token]);

  if (!analytics && !error) {
    return <LoadingScreen />;
  }

  return (
    <section className="page-container">
      <header className="page-header dashboard-header">
        <div>
          <p className="eyebrow">ADMIN WORKSPACE</p>
          <h1>Hiring dashboard</h1>
          <p>
            Signed in as {user.email}. Manage jobs and move
            candidates through the hiring pipeline.
          </p>
        </div>

        <Link className="primary-button" to="/admin/jobs/new">
          Create job
        </Link>
      </header>

      {error ? <ErrorMessage message={error} /> : null}

      {analytics ? (
        <>
          <div className="analytics-grid">
            <article className="analytics-card card">
              <p className="eyebrow">HIRING ROLES</p>
              <strong className="analytics-value">
                {analytics.jobs.total}
              </strong>
              <h2>Total jobs</h2>
              <p>
                Hiring opportunities created from your administrator
                account.
              </p>

              <Link className="text-link" to="/admin/jobs">
                Manage jobs
                <span aria-hidden="true"> →</span>
              </Link>
            </article>

            <article className="analytics-card card">
              <p className="eyebrow">ACTIVE HIRING</p>
              <strong className="analytics-value">
                {analytics.jobs.open}
              </strong>
              <h2>Open jobs</h2>
              <p>
                Roles currently visible to candidates for discovery
                and applications.
              </p>

              <Link className="text-link" to="/admin/jobs">
                Review active roles
                <span aria-hidden="true"> →</span>
              </Link>
            </article>

            <article className="analytics-card card">
              <p className="eyebrow">CANDIDATE PIPELINE</p>
              <strong className="analytics-value">
                {analytics.applications.total}
              </strong>
              <h2>Total applications</h2>
              <p>
                Candidate applications received across your hiring
                opportunities.
              </p>

              <Link className="text-link" to="/admin/jobs">
                Review applicants
                <span aria-hidden="true"> →</span>
              </Link>
            </article>
          </div>

          <section className="pipeline-section card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">HIRING PIPELINE</p>
                <h2>Application status overview</h2>
              </div>

              <Link className="text-link" to="/admin/jobs">
                Open job management
                <span aria-hidden="true"> →</span>
              </Link>
            </div>

            <div className="pipeline-grid">
              <article className="pipeline-stat">
                <span>Applied</span>
                <strong>{analytics.applications.applied}</strong>
              </article>

              <article className="pipeline-stat">
                <span>Shortlisted</span>
                <strong>
                  {analytics.applications.shortlisted}
                </strong>
              </article>

              <article className="pipeline-stat">
                <span>Rejected</span>
                <strong>{analytics.applications.rejected}</strong>
              </article>

              <article className="pipeline-stat">
                <span>Closed jobs</span>
                <strong>{analytics.jobs.closed}</strong>
              </article>
            </div>
          </section>
        </>
      ) : null}

      <div className="dashboard-grid">
        <article className="dashboard-card">
          <span>Job management</span>
          <h2>Create and manage hiring opportunities</h2>
          <p>
            Publish jobs, review active and closed roles, and control
            candidate availability.
          </p>

          <Link className="primary-button" to="/admin/jobs">
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

          <Link className="secondary-button" to="/admin/jobs">
            Review applicants
          </Link>
        </article>
      </div>
    </section>
  );
}
