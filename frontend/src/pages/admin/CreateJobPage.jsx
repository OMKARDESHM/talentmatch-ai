import { useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import { createJob } from "../../api/adminJobsApi";
import { useAuth } from "../../auth/useAuth";
import ErrorMessage from "../../components/ErrorMessage";

const INITIAL_FORM = {
  title: "",
  description: "",
  required_skills: "",
  experience_level: "",
  location: "",
  role_type: "",
  domain: "",
};

export default function CreateJobPage() {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState(INITIAL_FORM);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((currentForm) => ({
      ...currentForm,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      setIsSubmitting(true);
      setError("");

      await createJob(token, formData);
      navigate("/admin/jobs");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">JOB MANAGEMENT</p>
          <h1>Create a job</h1>
          <p>
            Publish a new open role for candidates to discover and
            match against.
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

      <form
        className="profile-form"
        onSubmit={handleSubmit}
      >
        <div className="form-grid">
          <label className="form-field">
            <span>Job title</span>
            <input
              name="title"
              type="text"
              minLength="2"
              maxLength="200"
              required
              value={formData.title}
              onChange={handleChange}
              placeholder="Python Backend Engineer"
            />
          </label>

          <label className="form-field">
            <span>Required skills</span>
            <input
              name="required_skills"
              type="text"
              required
              value={formData.required_skills}
              onChange={handleChange}
              placeholder="Python, FastAPI, PostgreSQL"
            />
          </label>

          <label className="form-field">
            <span>Experience level</span>
            <input
              name="experience_level"
              type="text"
              minLength="2"
              maxLength="50"
              required
              value={formData.experience_level}
              onChange={handleChange}
              placeholder="Entry Level"
            />
          </label>

          <label className="form-field">
            <span>Location</span>
            <input
              name="location"
              type="text"
              minLength="2"
              maxLength="150"
              required
              value={formData.location}
              onChange={handleChange}
              placeholder="Pune"
            />
          </label>

          <label className="form-field">
            <span>Role type</span>
            <input
              name="role_type"
              type="text"
              minLength="2"
              maxLength="100"
              required
              value={formData.role_type}
              onChange={handleChange}
              placeholder="Backend"
            />
          </label>

          <label className="form-field">
            <span>Domain</span>
            <input
              name="domain"
              type="text"
              minLength="2"
              maxLength="100"
              required
              value={formData.domain}
              onChange={handleChange}
              placeholder="Healthcare"
            />
          </label>
        </div>

        <label className="form-field">
          <span>Description</span>
          <textarea
            name="description"
            minLength="10"
            required
            rows="7"
            value={formData.description}
            onChange={handleChange}
            placeholder={
              "Describe the role, responsibilities, and hiring context."
            }
          />
        </label>

        <div className="form-actions">
          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Creating job..." : "Create job"}
          </button>

          <Link
            className="secondary-button"
            to="/admin/jobs"
          >
            Cancel
          </Link>
        </div>
      </form>
    </section>
  );
}
