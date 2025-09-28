import { ApiError } from './api-error';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export function computeApiBaseOrigin(apiBaseUrl: string): string {
  try {
    const url = new URL(apiBaseUrl);
    let pathname = url.pathname.replace(/\/+$/, "");
    if (pathname.endsWith("/api")) {
      pathname = pathname.slice(0, -4) || "";
    }
    return `${url.origin}${pathname}`.replace(/\/$/, "");
  } catch (_error) {
    console.error('Error:' + _error);
    return apiBaseUrl.replace(/\/$/, "");
  }
}

export const API_BASE_ORIGIN = computeApiBaseOrigin(API_BASE_URL);

export function resolveMediaUrl(path?: string | null): string | undefined {
  if (!path) return undefined;
  if (/^https?:\/\//i.test(path)) return path;
  const base = API_BASE_ORIGIN.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return base ? `${base}${normalizedPath}` : normalizedPath;
}

export function buildWebSocketUrl(
  path: string,
  params: Record<string, string | undefined | null> = {}
): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const originUrl = new URL(API_BASE_ORIGIN);
  originUrl.protocol = originUrl.protocol === "https:" ? "wss:" : "ws:";
  originUrl.pathname = normalizedPath;
  originUrl.search = "";
  originUrl.hash = "";
  const url = new URL(originUrl);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });
  return url.toString();
}

export async function apiFetch<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  // Get token from auth store if available
  let authToken: string | null = null;

  if (typeof window !== "undefined") {
    try {
      const authStorage = localStorage.getItem("auth-storage");
      if (authStorage) {
        const parsed = JSON.parse(authStorage);
        authToken = parsed.state?.token || null;
      }
    } catch {
      // Ignore localStorage errors
    }
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // Merge existing headers if provided
  if (init?.headers) {
    Object.assign(headers, init.headers);
  }

  // Add auth header if token exists
  if (authToken) {
    headers.Authorization = `Token ${authToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${typeof input === "string" ? input : input.toString()}`, {
    headers,
    ...init,
  });

  if (!response.ok) {
    let errorData: unknown = null;
    let errorMessage = response.statusText;

    try {
      const errorBody = await response.text();

      // Try to parse as JSON first
      try {
        errorData = JSON.parse(errorBody);

        // Extract message for backwards compatibility
        if (typeof errorData === 'object' && errorData !== null) {
          const data = errorData as Record<string, unknown>;
          if (data.detail && typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (data.message && typeof data.message === 'string') {
            errorMessage = data.message;
          } else if (data.error && typeof data.error === 'string') {
            errorMessage = data.error;
          }
        }
      } catch {
        // If not JSON, use the raw text
        errorMessage = errorBody || response.statusText;
        errorData = errorBody;
      }
    } catch {
      // If we can't read the response body, use status text
      errorMessage = response.statusText;
    }

    // Handle 401 Unauthorized - token might be invalid
    if (response.status === 401 && typeof window !== "undefined") {
      // Clear invalid token from storage
      localStorage.removeItem("auth-storage");
      console.warn("Authentication failed - token may be invalid");
    }

    throw new ApiError(errorMessage, response.status, errorData);
  }

  return response.json() as Promise<T>;
}
