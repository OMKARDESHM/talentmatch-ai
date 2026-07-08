import { apiRequest } from "./client";

export function getJobApplications(
  token,
  jobId,
  signal = null,
) {
  return apiRequest(
    `/admin/applications/jobs/${jobId}`,
    {
      token,
      signal,
    },
  );
}

export function updateApplicationStatus(
  token,
  applicationId,
  status,
) {
  return apiRequest(
    `/admin/applications/${applicationId}/status`,
    {
      method: "PATCH",
      token,
      body: {
        status,
      },
    },
  );
}
