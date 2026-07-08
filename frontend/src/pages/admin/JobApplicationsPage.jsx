import {
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  Link,
  useParams,
} from "react-router-dom";

import {
  getJobApplications,
  updateApplicationStatus,
} from "../../api/adminApplicationsApi";
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

export default function JobApplicationsPage() {
  const { token } = useAuth();
  const { jobId } = useParams();

  const [job, setJob] = useState(null);
  const [applications, setApplications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingApplicationId, setUpdatingApplicationId] =
    useState(null);

  const loadPage = useCallback(
    async (signal = null) => {
      try {
        setError("");

        const [jobData, applicationData] = await Promise.all([
          getJob(token, jobId, signal),
          getJobApplications(token, jobId, signal),
        ]);

        setJob(jobData);
        setApplications(applicationData);
      } catch (requestError) {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
        }
      } finally {
        if (!signal?.aborted) {
          setIsLoading(false);
        }
      }
    },
    [jobId, token],
  );

  useEffect(() => {
    const controller = new AbortController();

    loadPage(controller.signal);

    return () => {
      controller.abort();
    };
  }, [loadPage]);

  async function handleStatusUpdate(
    applicationId,
    status,
  ) {
    try {
      setUpdatingApplicationId(applicationId);
      setError("");

      const updatedApplication =
        await updateApplicationStatus(
          token,
          applicationId,
          status,
        );

      setApplications((currentApplications) =>
        currentApplications.map((application) =>
          application.id === updatedApplication.id
            ? updatedApplication
            : application,
        ),
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setUpdatingApplicationId(null);
    }
  }

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <section className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">APPLICATION PIPELINE</p>
          <h1>{job?.title ?? "Job applications"}</h1>
          <p>
            Review the candidate profile snapshot captured when each
            application was submitted.
          </p>
        </div>

        <Link
          className="secondary-button"
          to="/admin/jobs"
        >
          Back to jobs
        </Link>
      </header>

      <ErrorMessage message={error} />

      {applications.length === 0 ? (
        <EmptyState
          title="No applications yet"
          description={
            "Candidates have not applied to this job yet."
          }
        />
      ) : (
        <div className="application-list">
          {applications.map((application) => {
            const snapshot = application.profile_snapshot ?? {};
            const isUpdating =
              updatingApplicationId === application.id;

            return (
              <article
                className="application-card"
                key={application.id}
              >
                <div className="job-card-header">
                  <div>
                    <p className="eyebrow">
                      CANDIDATE #{application.candidate_id}
                    </p>
                    <h2>
                      {snapshot.name ?? "Candidate profile"}
                    </h2>
                  </div>

                  <StatusBadge status={application.status} />
                </div>

                <dl className="detail-grid">
                  <div>
                    <dt>Skills</dt>
                    <dd>{snapshot.skills || "Not provided"}</dd>
                  </div>

                  <div>
                    <dt>Education</dt>
                    <dd>{snapshot.education || "Not provided"}</dd>
                  </div>

                  <div>
                    <dt>Preferred location</dt>
                    <dd>
                      {snapshot.preferred_location ||
                        "Not provided"}
                    </dd>
                  </div>

                  <div>
                    <dt>Preferred role</dt>
                    <dd>
                      {snapshot.preferred_role_type ||
                        "Not provided"}
                    </dd>
                  </div>

                  <div>
                    <dt>Domain interest</dt>
                    <dd>
                      {snapshot.domain_interest || "Not provided"}
                    </dd>
                  </div>

                  <div>
                    <dt>Applied</dt>
                    <dd>{formatDate(application.applied_at)}</dd>
                  </div>
                </dl>

                <div className="snapshot-summary">
                  <strong>Project summary</strong>
                  <p>
                    {snapshot.project_summaries ||
                      "No project summary provided."}
                  </p>
                </div>

                <div className="card-actions">
                  <button
                    className="primary-button"
                    type="button"
                    disabled={
                      isUpdating ||
                      application.status === "shortlisted"
                    }
                    onClick={() =>
                      handleStatusUpdate(
                        application.id,
                        "shortlisted",
                      )
                    }
                  >
                    {isUpdating
                      ? "Updating..."
                      : "Shortlist"}
                  </button>

                  <button
                    className="secondary-button"
                    type="button"
                    disabled={
                      isUpdating ||
                      application.status === "rejected"
                    }
                    onClick={() =>
                      handleStatusUpdate(
                        application.id,
                        "rejected",
                      )
                    }
                  >
                    {isUpdating ? "Updating..." : "Reject"}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
