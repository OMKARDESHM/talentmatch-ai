import { useEffect, useState } from "react";

import { applyToJob } from "../../api/applicationsApi";
import { getJobs } from "../../api/jobsApi";
import { useAuth } from "../../auth/useAuth";
import EmptyState from "../../components/EmptyState";
import ErrorMessage from "../../components/ErrorMessage";
import LoadingScreen from "../../components/LoadingScreen";

const EMPTY_FILTERS = {
  skill: "",
  location: "",
  experienceLevel: "",
};

export default function JobSearchPage() {
  const { token } = useAuth();
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [activeFilters, setActiveFilters] =
    useState(EMPTY_FILTERS);
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [applyingJobId, setApplyingJobId] = useState(null);
  const [appliedJobIds, setAppliedJobIds] = useState([]);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadJobs() {
      setIsLoading(true);

      try {
        setError("");

        const data = await getJobs(
          token,
          activeFilters,
          controller.signal,
        );

        setJobs(data);
      } catch (requestError) {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
        }
      } finally {
        setIsLoading(false);
      }
    }

    loadJobs();

    return () => {
      controller.abort();
    };
  }, [token, activeFilters]);

  function handleFilterChange(event) {
    const { name, value } = event.target;

    setFilters((currentFilters) => ({
      ...currentFilters,
      [name]: value,
    }));
  }

  function handleSearch(event) {
    event.preventDefault();
    setSuccessMessage("");
    setActiveFilters({ ...filters });
  }

  function handleClearFilters() {
    setFilters(EMPTY_FILTERS);
    setActiveFilters(EMPTY_FILTERS);
    setSuccessMessage("");
  }

  async function handleApply(job) {
    setApplyingJobId(job.id);
    setError("");
    setSuccessMessage("");

    try {
      await applyToJob(token, job.id);

      setAppliedJobIds((currentIds) => [
        ...currentIds,
        job.id,
      ]);

      setSuccessMessage(
        `Application submitted for ${job.title}.`,
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setApplyingJobId(null);
    }
  }

  return (
    <section className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">JOB DISCOVERY</p>
          <h1>Search open opportunities</h1>
          <p>
            Filter current jobs by skill, location, or experience
            level and apply with your saved candidate profile.
          </p>
        </div>
      </header>

      <form className="filter-panel card" onSubmit={handleSearch}>
        <div className="filter-grid">
          <label className="form-field">
            <span>Skill</span>
            <input
              name="skill"
              value={filters.skill}
              onChange={handleFilterChange}
              placeholder="Python"
            />
          </label>

          <label className="form-field">
            <span>Location</span>
            <input
              name="location"
              value={filters.location}
              onChange={handleFilterChange}
              placeholder="Pune"
            />
          </label>

          <label className="form-field">
            <span>Experience level</span>
            <input
              name="experienceLevel"
              value={filters.experienceLevel}
              onChange={handleFilterChange}
              placeholder="Entry Level"
            />
          </label>
        </div>

        <div className="form-actions">
          <button className="primary-button" type="submit">
            Search jobs
          </button>

          <button
            className="secondary-button"
            type="button"
            onClick={handleClearFilters}
          >
            Clear filters
          </button>
        </div>
      </form>

      <ErrorMessage message={error} />

      {successMessage ? (
        <div className="success-message" role="status">
          {successMessage}
        </div>
      ) : null}

      {isLoading ? <LoadingScreen /> : null}

      {!isLoading && jobs.length === 0 ? (
        <EmptyState
          title="No jobs found"
          description="Try changing your filters to discover more open opportunities."
        />
      ) : null}

      {!isLoading && jobs.length > 0 ? (
        <div className="job-grid">
          {jobs.map((job) => {
            const hasApplied = appliedJobIds.includes(job.id);

            return (
              <article className="job-card card" key={job.id}>
                <div className="job-card-header">
                  <div>
                    <span className="job-domain">{job.domain}</span>
                    <h2>{job.title}</h2>
                  </div>

                  <span className="open-job-badge">Open</span>
                </div>

                <p className="job-description">
                  {job.description}
                </p>

                <dl className="job-details">
                  <div>
                    <dt>Skills</dt>
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

                <button
                  className="primary-button"
                  type="button"
                  disabled={
                    applyingJobId === job.id || hasApplied
                  }
                  onClick={() => handleApply(job)}
                >
                  {hasApplied
                    ? "Applied"
                    : applyingJobId === job.id
                      ? "Applying..."
                      : "Apply now"}
                </button>
              </article>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}