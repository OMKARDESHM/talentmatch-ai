import { apiRequest } from "./client";

export function getMyApplications(token, signal = null) {
  return apiRequest("/applications/me", {
    token,
    signal,
  });
}

export function applyToJob(token, jobId) {
  return apiRequest("/applications", {
    method: "POST",
    token,
    body: {
      job_id: jobId,
    },
  });
}