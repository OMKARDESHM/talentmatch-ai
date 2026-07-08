import {
  Navigate,
  Outlet,
  useLocation,
} from "react-router-dom";

import LoadingScreen from "../components/LoadingScreen";
import SessionRecoveryScreen from "../components/SessionRecoveryScreen";
import { useAuth } from "./useAuth";

export default function ProtectedRoute({ allowedRole }) {
  const {
    user,
    isAuthenticated,
    isInitializing,
    sessionRestoreError,
    retrySessionRestore,
    logout,
  } = useAuth();
  const location = useLocation();

  if (isInitializing) {
    return (
      <LoadingScreen message="Restoring your TalentMatch session..." />
    );
  }

  if (sessionRestoreError) {
    return (
      <SessionRecoveryScreen
        message={sessionRestoreError}
        isRetrying={isInitializing}
        onRetry={retrySessionRestore}
        onSignOut={logout}
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  if (allowedRole && user.role !== allowedRole) {
    const destination =
      user.role === "admin"
        ? "/admin"
        : "/candidate";

    return <Navigate to={destination} replace />;
  }

  return <Outlet />;
}
