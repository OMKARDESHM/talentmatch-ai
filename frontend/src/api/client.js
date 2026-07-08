const DEFAULT_API_BASE_URL = "/api";

function normalizeApiBaseUrl(value) {
  const normalizedValue = value?.trim();

  if (!normalizedValue) {
    return DEFAULT_API_BASE_URL;
  }

  return normalizedValue.replace(/\/+$/, "");
}

const API_BASE_URL = normalizeApiBaseUrl(
  import.meta.env.VITE_API_BASE_URL,
);

export class ApiError extends Error {
  constructor(message, status, details = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function parseResponse(response) {
  const contentType =
    response.headers.get("content-type") ?? "";

  if (!contentType.includes("application/json")) {
    return null;
  }

  return response.json();
}

export async function apiRequest(
  path,
  {
    method = "GET",
    token = null,
    body = null,
    signal = null,
  } = {},
) {
  const headers = {
    Accept: "application/json",
  };

  if (body !== null) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body === null ? null : JSON.stringify(body),
      signal,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw error;
    }

    throw new ApiError(
      "Unable to connect to the TalentMatch API.",
      0,
    );
  }

  const data = await parseResponse(response);

  if (!response.ok) {
    const message =
      typeof data?.detail === "string"
        ? data.detail
        : "The request could not be completed.";

    throw new ApiError(
      message,
      response.status,
      data,
    );
  }

  return data;
}
