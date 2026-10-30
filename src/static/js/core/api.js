/**
 * api.js -- Unified HTTP Client for HMS REST APIs
 * Handles JSON serialization, 401 unauthenticated redirect, 403 permission alerts, and toast errors.
 */

export async function apiRequest(endpoint, options = {}) {
  const url = endpoint.startsWith("/api") || endpoint.startsWith("/") ? endpoint : `/api/${endpoint}`;
  
  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    ...(options.headers || {})
  };

  const config = {
    ...options,
    headers,
    credentials: "same-origin"
  };

  if (config.body && typeof config.body === "object" && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
  }

  try {
    const response = await fetch(url, config);

    // Handle 401 Unauthorized / Session Timeout
    if (response.status === 401) {
      const data = await response.json().catch(() => ({}));
      if (data.timed_out) {
        window.dispatchEvent(new CustomEvent("hms:session-timeout", { detail: data }));
      } else {
        // Redirect to login page if on protected page
        if (!window.location.pathname.includes("/login")) {
          window.location.href = "/login";
        }
      }
      throw new Error(data.error || "Authentication required");
    }

    // Handle 403 Forbidden
    if (response.status === 403) {
      const data = await response.json().catch(() => ({}));
      window.dispatchEvent(new CustomEvent("hms:forbidden", { detail: data }));
      throw new Error(data.error || "Permission denied for this action");
    }

    // Handle other errors
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      const msg = data.error || data.message || `Request failed with status ${response.status}`;
      throw new Error(msg);
    }

    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return await response.json();
    }
    return await response.text();
  } catch (error) {
    console.error(`[API Error] ${options.method || 'GET'} ${url}:`, error);
    throw error;
  }
}

export const api = {
  get: (url, headers) => apiRequest(url, { method: "GET", headers }),
  post: (url, body, headers) => apiRequest(url, { method: "POST", body, headers }),
  put: (url, body, headers) => apiRequest(url, { method: "PUT", body, headers }),
  delete: (url, headers) => apiRequest(url, { method: "DELETE", headers })
};

