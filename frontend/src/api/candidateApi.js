import { apiRequest } from "./client";

export function getCandidateProfile(token, signal = null) {
  return apiRequest("/candidates/me", {
    token,
    signal,
  });
}

export function updateCandidateProfile(token, profileData) {
  return apiRequest("/candidates/me", {
    method: "PUT",
    token,
    body: profileData,
  });
}