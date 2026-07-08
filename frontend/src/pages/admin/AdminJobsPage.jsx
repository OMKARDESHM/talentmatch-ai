import {
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  getAdminJobs,
  updateJobStatus,
} from "../../api/adminJobsApi";
import { useAuth } from "../../auth/useAuth";
import EmptyState from "../../components/EmptyState";
import ErrorMessage from "../../components/ErrorMessage";
import LoadingScreen from "../../components/LoadingScreen";
import StatusBadge from "../../components/StatusBadge";

export default function AdminJobsPage() {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingJobId, setUpdatingJobId] = useState(null);

  const loadJobs = useCallback(
    async (signal = null) => {
      try {
        setError("");

        const data = await getAdminJobs(token, signal);
        setJobs(data);
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
    [token],
  );

  useEffect(() => {
    const controller = new AbortController();

    loadJobs(controller.signal);

    return () => {
      controller.abort();
    };
  }, [loadJobs]);

  async function handleStatusChange(job) {
    const nextStatus =
      job.status === "open" ? "closed" : "open";

    try {
      setUpdatingJobId(job.id);
      setError("");

      const updatedJob = await updateJobStatus(
        token,
        job.id,
        nextStatus,
      );

      setJobs((currentJobs) =>
        currentJobs.map((currentJob) =>
          currentJob.id === updatedJob.id
            ? updatedJob
            : currentJob,
        ),
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setUpdatingJobId(null);
    }
  }

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <section className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">ADMIN WORKSPACE</p>
          <h1>Manage jobs</h1>
          <p>
            Create hiring opportunities, control job availability,
            and review applicants for every role.
          </p>
        </div>

        <Link
          className="primary-button"
          to="/admin/jobs/new"
        >
          Create job
        </Link>
      </header>

      <ErrorMessage message={error} />

      {jobs.length === 0 ? (
        <EmptyState
          title="No jobs created yet"
          description={
            "Create your first job to begin receiving candidate applications."
          }
          action={
            <Link
              className="primary-button"
              to="/admin/jobs/new"
            >
              Create first job
            </Link>
          }
        />
      ) : (
        <div className="job-grid">
          {jobs.map((job) => (
            <article className="job-card" key={job.id}>
              <div className="job-card-header">
                <div>
                  <p className="eyebrow">{job.domain}</p>
                  <h2>{job.title}</h2>
                </div>

                <StatusBadge status={job.status} />
              </div>

              <p>{job.description}</p>

              <dl className="detail-grid">
                <div>
                  <dt>Required skills</dt>
                  <dd>{job.required_skills}</dd>
                </div>

                <div>
                  <dt>Experience</dt>
                  <dd>{job.experience_level}</dd>
                </div>

                <div>
                  <dt>Location</dt>
                  <dd>{job.location}</dd>
                </div>

                <div>
                  <dt>Role type</dt>
                  <dd>{job.role_type}</dd>
                </div>
              </dl>

              <div className="card-actions">
                <button
                  className="primary-button"
                  type="button"
                  onClick={() =>
                    navigate(
                      `/admin/jobs/${job.id}/applications`,
                    )
                  }
                >
                  View applicants
                </button>

                <button
                  className="secondary-button"
                  type="button"
                  disabled={updatingJobId === job.id}
                  onClick={() => handleStatusChange(job)}
                >
                  {updatingJobId === job.id
                    ? "Updating..."
                    : job.status === "open"
                      ? "Close job"
                      : "Reopen job"}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
