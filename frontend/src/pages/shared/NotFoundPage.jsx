import { Link } from "react-router-dom";

import { useAuth } from "../../auth/useAuth";

export default function NotFoundPage() {
  const { user, isAuthenticated } = useAuth();

  const destination = isAuthenticated
    ? user.role === "admin"
      ? "/admin"
      : "/candidate"
    : "/login";

  return (
    <main className="not-found-page">
      <div className="not-found-card">
        <p className="eyebrow">404</p>
        <h1>Page not found</h1>
        <p>
          The page you requested does not exist in this workspace.
        </p>

        <Link
          className="primary-button link-button"
          to={destination}
        >
          Return to workspace
        </Link>
      </div>
    </main>
  );
}