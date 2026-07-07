import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import { useAuth } from "./auth/useAuth";
import ProtectedRoute from "./auth/ProtectedRoute";
import LoadingScreen from "./components/LoadingScreen";
import AppLayout from "./layouts/AppLayout";
import AdminDashboardPage from "./pages/admin/AdminDashboardPage";
import CandidateDashboardPage from "./pages/candidate/CandidateDashboardPage";
import CandidateProfilePage from "./pages/candidate/CandidateProfilePage";
import JobMatchingPage from "./pages/candidate/JobMatchingPage";
import JobSearchPage from "./pages/candidate/JobSearchPage";
import MyApplicationsPage from "./pages/candidate/MyApplicationsPage";
import LoginPage from "./pages/shared/LoginPage";
import NotFoundPage from "./pages/shared/NotFoundPage";

function HomeRedirect() {
  const {
    user,
    isAuthenticated,
    isInitializing,
  } = useAuth();

  if (isInitializing) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Navigate
      to={
        user.role === "admin"
          ? "/admin"
          : "/candidate"
      }
      replace
    />
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/login" element={<LoginPage />} />

      <Route
        element={<ProtectedRoute allowedRole="candidate" />}
      >
        <Route element={<AppLayout />}>
          <Route
            path="/candidate"
            element={<CandidateDashboardPage />}
          />
          <Route
            path="/candidate/profile"
            element={<CandidateProfilePage />}
          />
          <Route
            path="/candidate/jobs"
            element={<JobSearchPage />}
          />
          <Route
            path="/candidate/matching"
            element={<JobMatchingPage />}
          />
          <Route
            path="/candidate/applications"
            element={<MyApplicationsPage />}
          />
        </Route>
      </Route>

      <Route
        element={<ProtectedRoute allowedRole="admin" />}
      >
        <Route element={<AppLayout />}>
          <Route
            path="/admin"
            element={<AdminDashboardPage />}
          />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}