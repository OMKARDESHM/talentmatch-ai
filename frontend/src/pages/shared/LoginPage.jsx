import { useEffect, useState } from "react";
import {
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";

import { ApiError } from "../../api/client";
import { useAuth } from "../../auth/useAuth";
import LoadingScreen from "../../components/LoadingScreen";

const DEMO_ACCOUNTS = {
  candidate: {
    email: "candidate@talentmatch.dev",
    password: "CandidatePass123!",
  },
  admin: {
    email: "admin@talentmatch.dev",
    password: "AdminPass123!",
  },
};

function getDashboardPath(role) {
  return role === "admin" ? "/admin" : "/candidate";
}

export default function LoginPage() {
  const {
    user,
    isAuthenticated,
    isInitializing,
    login,
  } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const [email, setEmail] = useState(
    DEMO_ACCOUNTS.candidate.email,
  );
  const [password, setPassword] = useState(
    DEMO_ACCOUNTS.candidate.password,
  );
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setErrorMessage("");
  }, [email, password]);

  if (isInitializing) {
    return <LoadingScreen />;
  }

  if (isAuthenticated) {
    return (
      <Navigate
        to={getDashboardPath(user.role)}
        replace
      />
    );
  }

 function selectDemoAccount(role) {
  const account = DEMO_ACCOUNTS[role];

  setEmail(account.email);
  setPassword(account.password);
}

  async function handleSubmit(event) {
    event.preventDefault();

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const authenticatedUser = await login(
        email.trim(),
        password,
      );

      const requestedPath = location.state?.from;
      const dashboardPath = getDashboardPath(
        authenticatedUser.role,
      );

      const canUseRequestedPath =
        typeof requestedPath === "string"
        && requestedPath.startsWith(
          `/${authenticatedUser.role}`,
        );

      navigate(
        canUseRequestedPath
          ? requestedPath
          : dashboardPath,
        {
          replace: true,
        },
      );
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage(
          "An unexpected error occurred while signing in.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-introduction">
        <div className="login-introduction-content">
          <div className="brand-lockup">
            <div className="brand-mark" aria-hidden="true">
              TM
            </div>
            <span>TalentMatch AI</span>
          </div>

          <p className="eyebrow">EXPLAINABLE JOB MATCHING</p>

          <h1>
            Find relevant opportunities with matching you can
            understand.
          </h1>

          <p className="login-description">
            TalentMatch combines candidate intent, profile context,
            and structured job data to rank open opportunities and
            explain every recommendation.
          </p>

          <div className="feature-grid">
            <article>
              <strong>Natural language intent</strong>
              <span>
                Describe the role, skills, location, and domain you
                want.
              </span>
            </article>

            <article>
              <strong>Explainable ranking</strong>
              <span>
                Review the exact relevance factors behind every
                match.
              </span>
            </article>

            <article>
              <strong>Application workflow</strong>
              <span>
                Apply with a profile snapshot and track pipeline
                progress.
              </span>
            </article>

            <article>
              <strong>Admin visibility</strong>
              <span>
                Manage jobs, applicants, and hiring pipeline status.
              </span>
            </article>
          </div>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <div className="login-card-heading">
            <p className="eyebrow">WELCOME BACK</p>
            <h2>Sign in to your workspace</h2>
            <p>
              Use a demo account or enter your credentials.
            </p>
          </div>

          <div className="demo-account-actions">
            <button
              type="button"
              className="demo-account-button"
              onClick={() => selectDemoAccount("candidate")}
            >
              Use candidate demo
            </button>

            <button
              type="button"
              className="demo-account-button"
              onClick={() => selectDemoAccount("admin")}
            >
              Use admin demo
            </button>
          </div>

          <form
            className="login-form"
            onSubmit={handleSubmit}
          >
            <label>
              Email address
              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                autoComplete="email"
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                autoComplete="current-password"
                required
              />
            </label>

            {errorMessage && (
              <div className="error-message" role="alert">
                {errorMessage}
              </div>
            )}

            <button
              className="primary-button"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Signing in..."
                : "Sign in"}
            </button>
          </form>

          <p className="demo-note">
            Demo credentials are seeded locally for evaluation.
          </p>
        </div>
      </section>
    </main>
  );
}