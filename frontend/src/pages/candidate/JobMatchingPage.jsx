import { useState } from "react";

import { applyToJob } from "../../api/applicationsApi";
import { matchJobs } from "../../api/matchingApi";
import { useAuth } from "../../auth/useAuth";
import EmptyState from "../../components/EmptyState";
import ErrorMessage from "../../components/ErrorMessage";

const EXAMPLE_QUERY =
  "Find Python backend jobs in Pune for entry level healthcare work";

function IntentGroup({ label, values }) {
  if (!values?.length) {
    return null;
  }

  return (
    <div className="intent-group">
      <strong>{label}</strong>

      <div className="tag-list">
        {values.map((value) => (
          <span className="intent-tag" key={`${label}-${value}`}>
            {value}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function JobMatchingPage() {
  const { token } = useAuth();
  const [query, setQuery] = useState(EXAMPLE_QUERY);
  const [matchResponse, setMatchResponse] = useState(null);
  const [isMatching, setIsMatching] = useState(false);
  const [applyingJobId, setApplyingJobId] = useState(null);
  const [appliedJobIds, setAppliedJobIds] = useState([]);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  async function handleMatch(event) {
    event.preventDefault();

    setIsMatching(true);
    setError("");
    setSuccessMessage("");

    try {
      const data = await matchJobs(token, query.trim());
      setMatchResponse(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsMatching(false);
    }
  }

  async function handleApply(match) {
    setApplyingJobId(match.job.id);
    setError("");
    setSuccessMessage("");

    try {
      await applyToJob(token, match.job.id);

      setAppliedJobIds((currentIds) => [
        ...currentIds,
        match.job.id,
      ]);

      setSuccessMessage(
        `Application submitted for ${match.job.title}.`,
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
          <p className="eyebrow">EXPLAINABLE MATCHING</p>
          <h1>Describe the job you want</h1>
          <p>
            Use natural language. TalentMatch interprets your intent,
            combines it with your candidate profile, and explains each
            ranked result.
          </p>
        </div>
      </header>

      <form className="matching-form card" onSubmit={handleMatch}>
        <label className="form-field">
          <span>What are you looking for?</span>
          <textarea
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            rows={5}
            minLength={3}
            maxLength={1000}
            required
          />
        </label>

        <div className="form-actions">
          <button
            className="primary-button"
            type="submit"
            disabled={isMatching}
          >
            {isMatching ? "Ranking jobs..." : "Find matching jobs"}
          </button>
        </div>
      </form>

      <ErrorMessage message={error} />

      {successMessage ? (
        <div className="success-message" role="status">
          {successMessage}
        </div>
      ) : null}

      {matchResponse ? (
        <>
          <section className="intent-panel card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">INTERPRETED INTENT</p>
                <h2>What TalentMatch understood</h2>
              </div>
            </div>

            <div className="intent-grid">
              <IntentGroup
                label="Skills"
                values={matchResponse.interpreted_intent.skills}
              />

              <IntentGroup
                label="Role types"
                values={
                  matchResponse.interpreted_intent.role_types
                }
              />

              <IntentGroup
                label="Domains"
                values={matchResponse.interpreted_intent.domains}
              />

              <IntentGroup
                label="Locations"
                values={
                  matchResponse.interpreted_intent.locations
                }
              />

              <IntentGroup
                label="Experience"
                values={
                  matchResponse.interpreted_intent
                    .experience_levels
                }
              />
            </div>
          </section>

          {matchResponse.matches.length === 0 ? (
            <EmptyState
              title="No matching jobs"
              description="Try describing a broader role, skill set, domain, or location."
            />
          ) : (
            <div className="match-list">
              {matchResponse.matches.map((match, index) => {
                const hasApplied = appliedJobIds.includes(
                  match.job.id,
                );

                return (
                  <article
                    className="match-card card"
                    key={match.job.id}
                  >
                    <div className="match-card-main">
                      <div className="match-rank">
                        #{index + 1}
                      </div>

                      <div className="match-content">
                        <span className="job-domain">
                          {match.job.domain}
                        </span>

                        <h2>{match.job.title}</h2>

                        <p>{match.job.description}</p>

                        <div className="match-explanation">
                          <strong>Why this job matched</strong>
                          <p>{match.explanation}</p>
                        </div>

                        <div className="tag-list">
                          {match.matched_factors.map((factor) => (
                            <span
                              className="factor-tag"
                              key={factor}
                            >
                              {factor}
                            </span>
                          ))}
                        </div>

                        <div className="job-meta-line">
                          <span>{match.job.location}</span>
                          <span>{match.job.role_type}</span>
                          <span>
                            {match.job.experience_level}
                          </span>
                        </div>

                        <button
                          className="primary-button"
                          type="button"
                          disabled={
                            applyingJobId === match.job.id ||
                            hasApplied
                          }
                          onClick={() => handleApply(match)}
                        >
                          {hasApplied
                            ? "Applied"
                            : applyingJobId === match.job.id
                              ? "Applying..."
                              : "Apply to this job"}
                        </button>
                      </div>
                    </div>

                    <div className="match-score">
                      <strong>{match.match_score}</strong>
                      <span>match score</span>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </>
      ) : null}
    </section>
  );
}