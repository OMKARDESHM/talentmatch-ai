import { Navigate, Outlet, useLocation } from "react-router-dom";

import LoadingScreen from "../components/LoadingScreen";
import { useAuth } from "./useAuth";

export default function ProtectedRoute({ allowedRole }) {
  const {
    user,
    isAuthenticated,
    isInitializing,
  } = useAuth();
  const location = useLocation();

  if (isInitializing) {
    return <LoadingScreen />;
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