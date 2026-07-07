import { useEffect, useState } from "react";

import { getMyApplications } from "../../api/applicationsApi";
import { getJob } from "../../api/jobsApi";
import { useAuth } from "../../auth/useAuth";
import EmptyState from "../../components/EmptyState";
import ErrorMessage from "../../components/ErrorMessage";
import LoadingScreen from "../../components/LoadingScreen";
import StatusBadge from "../../components/StatusBadge";

function formatDate(value) {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function MyApplicationsPage() {
  const { token } = useAuth();
  const [applications, setApplications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadApplications() {
      try {
        setError("");

        const applicationData = await getMyApplications(
          token,
          controller.signal,
        );

        const applicationsWithJobs = await Promise.all(
          applicationData.map(async (application) => {
            const job = await getJob(
              token,
              application.job_id,
              controller.signal,
            );

            return {
              ...application,
              job,
            };
          }),
        );

        setApplications(applicationsWithJobs);
      } catch (requestError) {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
        }
      } finally {
        setIsLoading(false);
      }
    }

    loadApplications();

    return () => {
      controller.abort();
    };
  }, [token]);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <section className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">APPLICATION TRACKER</p>
          <h1>My applications</h1>
          <p>
            Review the jobs you applied to and follow each application
            through the hiring pipeline.
          </p>
        </div>
      </header>

      <ErrorMessage message={error} />

      {!error && applications.length === 0 ? (
        <EmptyState
          title="No applications yet"
          description="Search or match jobs and submit your first application."
        />
      ) : null}

      {applications.length > 0 ? (
        <div className="application-list">
          {applications.map((application) => (
            <article
              className="application-card card"
              key={application.id}
            >
              <div className="application-card-header">
                <div>
                  <span className="job-domain">
                    {application.job.domain}
                  </span>
                  <h2>{application.job.title}</h2>
                </div>

                <StatusBadge status={application.status} />
              </div>

              <p>{application.job.description}</p>

              <dl className="job-details">
                <div>
                  <dt>Location</dt>
                  <dd>{application.job.location}</dd>
                </div>

                <div>
                  <dt>Role type</dt>
                  <dd>{application.job.role_type}</dd>
                </div>

                <div>
                  <dt>Required skills</dt>
                  <dd>{application.job.required_skills}</dd>
                </div>

                <div>
                  <dt>Applied</dt>
                  <dd>{formatDate(application.applied_at)}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}