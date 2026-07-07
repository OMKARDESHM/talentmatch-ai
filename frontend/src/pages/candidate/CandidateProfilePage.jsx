import { useEffect, useState } from "react";

import {
  getCandidateProfile,
  updateCandidateProfile,
} from "../../api/candidateApi";
import { useAuth } from "../../auth/useAuth";
import ErrorMessage from "../../components/ErrorMessage";
import LoadingScreen from "../../components/LoadingScreen";

const EMPTY_PROFILE = {
  name: "",
  skills: "",
  education: "",
  project_summaries: "",
  preferred_location: "",
  preferred_role_type: "",
  domain_interest: "",
};

export default function CandidateProfilePage() {
  const { token } = useAuth();
  const [profile, setProfile] = useState(EMPTY_PROFILE);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadProfile() {
      try {
        setError("");

        const data = await getCandidateProfile(
          token,
          controller.signal,
        );

        setProfile(data);
      } catch (requestError) {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
        }
      } finally {
        setIsLoading(false);
      }
    }

    loadProfile();

    return () => {
      controller.abort();
    };
  }, [token]);

  function handleChange(event) {
    const { name, value } = event.target;

    setProfile((currentProfile) => ({
      ...currentProfile,
      [name]: value,
    }));

    setSuccessMessage("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setIsSaving(true);
    setError("");
    setSuccessMessage("");

    try {
      const updatedProfile = await updateCandidateProfile(
        token,
        {
          name: profile.name.trim(),
          skills: profile.skills.trim(),
          education: profile.education.trim(),
          project_summaries: profile.project_summaries.trim(),
          preferred_location: profile.preferred_location.trim(),
          preferred_role_type:
            profile.preferred_role_type.trim(),
          domain_interest: profile.domain_interest.trim(),
        },
      );

      setProfile(updatedProfile);
      setSuccessMessage("Profile updated successfully.");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <section className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">CANDIDATE PROFILE</p>
          <h1>Build your matching profile</h1>
          <p>
            Keep your skills, preferences, and project experience
            current. TalentMatch uses this profile when ranking jobs.
          </p>
        </div>
      </header>

      <ErrorMessage message={error} />

      {successMessage ? (
        <div className="success-message" role="status">
          {successMessage}
        </div>
      ) : null}

      <form className="profile-form card" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label className="form-field">
            <span>Name</span>
            <input
              name="name"
              value={profile.name}
              onChange={handleChange}
              minLength={2}
              maxLength={100}
              required
            />
          </label>

          <label className="form-field">
            <span>Preferred location</span>
            <input
              name="preferred_location"
              value={profile.preferred_location}
              onChange={handleChange}
              maxLength={100}
              required
            />
          </label>

          <label className="form-field">
            <span>Preferred role type</span>
            <input
              name="preferred_role_type"
              value={profile.preferred_role_type}
              onChange={handleChange}
              maxLength={100}
              required
            />
          </label>

          <label className="form-field">
            <span>Domain interest</span>
            <input
              name="domain_interest"
              value={profile.domain_interest}
              onChange={handleChange}
              maxLength={100}
              required
            />
          </label>
        </div>

        <label className="form-field">
          <span>Skills</span>
          <textarea
            name="skills"
            value={profile.skills}
            onChange={handleChange}
            rows={4}
            maxLength={1000}
            placeholder="Python, FastAPI, SQL, React"
            required
          />
          <small>
            Use clear technology and skill names separated by commas.
          </small>
        </label>

        <label className="form-field">
          <span>Education</span>
          <textarea
            name="education"
            value={profile.education}
            onChange={handleChange}
            rows={4}
            maxLength={1000}
            required
          />
        </label>

        <label className="form-field">
          <span>Project summaries</span>
          <textarea
            name="project_summaries"
            value={profile.project_summaries}
            onChange={handleChange}
            rows={7}
            maxLength={3000}
            required
          />
        </label>

        <div className="form-actions">
          <button
            className="primary-button"
            type="submit"
            disabled={isSaving}
          >
            {isSaving ? "Saving profile..." : "Save profile"}
          </button>
        </div>
      </form>
    </section>
  );
}