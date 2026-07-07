import { apiRequest } from "./client";

function buildJobSearchParams(filters = {}) {
  const searchParams = new URLSearchParams();

  if (filters.skill?.trim()) {
    searchParams.set("skill", filters.skill.trim());
  }

  if (filters.location?.trim()) {
    searchParams.set("location", filters.location.trim());
  }

  if (filters.experienceLevel?.trim()) {
    searchParams.set(
      "experience_level",
      filters.experienceLevel.trim(),
    );
  }

  return searchParams;
}

export function getJobs(
  token,
  filters = {},
  signal = null,
) {
  const searchParams = buildJobSearchParams(filters);
  const query = searchParams.toString();
  const path = query ? `/jobs?${query}` : "/jobs";

  return apiRequest(path, {
    token,
    signal,
  });
}

export function getJob(token, jobId, signal = null) {
  return apiRequest(`/jobs/${jobId}`, {
    token,
    signal,
  });
}
