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

export async function apiFetch<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${typeof input === "string" ? input : input.toString()}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || response.statusText);
  }

  return response.json() as Promise<T>;
}
