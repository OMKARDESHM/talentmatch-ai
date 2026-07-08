import { apiRequest } from "./client";

export function getAdminJobs(token, signal = null) {
  return apiRequest("/admin/jobs", {
    token,
    signal,
  });
}

export function createJob(token, jobData) {
  return apiRequest("/jobs", {
    method: "POST",
    token,
    body: jobData,
  });
}

export function updateJobStatus(
  token,
  jobId,
  status,
) {
  return apiRequest(`/jobs/${jobId}/status`, {
    method: "PATCH",
    token,
    body: {
      status,
    },
  });
}
