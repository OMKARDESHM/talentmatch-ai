import { apiRequest } from "./client";

export function getCandidateDashboardAnalytics(
  token,
  signal = null,
) {
  return apiRequest("/analytics/candidate/dashboard", {
    token,
    signal,
  });
}

export function getAdminDashboardAnalytics(
  token,
  signal = null,
) {
  return apiRequest("/analytics/admin/dashboard", {
    token,
    signal,
  });
}
