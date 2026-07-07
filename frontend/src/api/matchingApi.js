import { apiRequest } from "./client";

export function matchJobs(token, query) {
  return apiRequest("/matching/jobs", {
    method: "POST",
    token,
    body: {
      query,
    },
  });
}