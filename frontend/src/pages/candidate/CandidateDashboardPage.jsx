import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getCandidateDashboardAnalytics } from "../../api/analyticsApi";
import { useAuth } from "../../auth/useAuth";
import ErrorMessage from "../../components/ErrorMessage";
import LoadingScreen from "../../components/LoadingScreen";

const WORKFLOWS = [
  {
    eyebrow: "PROFILE",
    title: "Keep your candidate profile current",
    description:
      "Update skills, education, project experience, preferred location, role type, and domain interests.",
    link: "/candidate/profile",
    action: "Edit profile",
  },
  {
    eyebrow: "DISCOVERY",
    title: "Search open jobs",
    description:
      "Filter current opportunities by skill, location, and experience level before applying.",
    link: "/candidate/jobs",
    action: "Search jobs",
  },
  {
    eyebrow: "MATCHING",
    title: "Use explainable job matching",
    description:
      "Describe the opportunity you want and review ranked jobs with match scores and explanations.",
    link: "/candidate/matching",
    action: "Match jobs",
  },
  {
    eyebrow: "APPLICATIONS",
    title: "Track your applications",
    description:
      "Review submitted applications and follow their current hiring status.",
    link: "/candidate/applications",
    action: "View applications",
  },
];

export default function CandidateDashboardPage() {
  const { token, user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadAnalytics() {
      try {
        setError("");

        const data = await getCandidateDashboardAnalytics(
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
          <p className="eyebrow">CANDIDATE WORKSPACE</p>
          <h1>Candidate dashboard</h1>
          <p>
            Signed in as {user.email}. Build your profile, discover
            opportunities, use explainable matching, and track every
            application.
          </p>
        </div>
      </header>

      {error ? <ErrorMessage message={error} /> : null}

      {analytics ? (
        <>
          <div className="analytics-grid">
            <article className="analytics-card card">
              <p className="eyebrow">PROFILE</p>
              <strong className="analytics-value">
                {analytics.profile_completeness}%
              </strong>
              <h2>Profile completeness</h2>
              <p>
                Complete candidate information improves the context
                available to the matching engine.
              </p>

              <div
                className="progress-track"
                aria-label={`Profile ${analytics.profile_completeness}% complete`}
              >
                <div
                  className="progress-value"
                  style={{
                    width: `${analytics.profile_completeness}%`,
                  }}
                />
              </div>

              <Link className="text-link" to="/candidate/profile">
                Complete profile
                <span aria-hidden="true"> →</span>
              </Link>
            </article>

            <article className="analytics-card card">
              <p className="eyebrow">OPPORTUNITIES</p>
              <strong className="analytics-value">
                {analytics.open_jobs}
              </strong>
              <h2>Open jobs</h2>
              <p>
                Current open opportunities available for candidate
                discovery and explainable matching.
              </p>

              <Link className="text-link" to="/candidate/jobs">
                Explore open jobs
                <span aria-hidden="true"> →</span>
              </Link>
            </article>

            <article className="analytics-card card">
              <p className="eyebrow">APPLICATIONS</p>
              <strong className="analytics-value">
                {analytics.applications.total}
              </strong>
              <h2>Total applications</h2>
              <p>
                Applications submitted from your candidate account.
              </p>

              <Link
                className="text-link"
                to="/candidate/applications"
              >
                Track applications
                <span aria-hidden="true"> →</span>
              </Link>
            </article>
          </div>

          <section className="pipeline-section card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">APPLICATION PIPELINE</p>
                <h2>Your hiring progress</h2>
              </div>

              <Link
                className="text-link"
                to="/candidate/applications"
              >
                View details
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
            </div>
          </section>
        </>
      ) : null}

      <div className="workflow-grid">
        {WORKFLOWS.map((workflow) => (
          <article className="workflow-card card" key={workflow.link}>
            <p className="eyebrow">{workflow.eyebrow}</p>
            <h2>{workflow.title}</h2>
            <p>{workflow.description}</p>

            <Link className="text-link" to={workflow.link}>
              {workflow.action}
              <span aria-hidden="true"> →</span>
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}
