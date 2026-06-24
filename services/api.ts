import type { NewsletterDraftInput, NewsletterSummary } from "@/types/newsletter";

export type ApiQuery = Record<string, string | number | boolean | null | undefined>;

export type ApiRequestOptions = Omit<RequestInit, "body"> & {
  body?: BodyInit | null;
  json?: unknown;
  query?: ApiQuery;
  timeoutMs?: number;
};

export type ApiClientOptions = {
  baseUrl?: string;
  fetcher?: typeof fetch;
};

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

const DEFAULT_TIMEOUT_MS = 15000;
const defaultBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function buildApiUrl(baseUrl: string, path: string, query?: ApiQuery) {
  const isAbsolute = /^https?:\/\//i.test(path);
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const fallbackBase = "http://newsletter.local";
  const url = isAbsolute
    ? new URL(path)
    : new URL(`${baseUrl.replace(/\/$/, "")}${normalizedPath}`, baseUrl ? undefined : fallbackBase);

  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.set(key, String(value));
    }
  });

  if (!baseUrl && !isAbsolute) {
    return `${url.pathname}${url.search}`;
  }

  return url.toString();
}

async function readResponse(response: Response) {
  if (response.status === 204) {
    return undefined;
  }

  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

export function createApiClient({ baseUrl = defaultBaseUrl, fetcher = fetch }: ApiClientOptions = {}) {
  async function request<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
    const { headers, json, query, timeoutMs = DEFAULT_TIMEOUT_MS, ...init } = options;
    const controller = init.signal ? undefined : new AbortController();
    const timeout = controller
      ? globalThis.setTimeout(() => controller.abort(), timeoutMs)
      : undefined;
    const requestHeaders = new Headers(headers);

    requestHeaders.set("Accept", "application/json");

    let body = init.body;
    if (json !== undefined) {
      requestHeaders.set("Content-Type", "application/json");
      body = JSON.stringify(json);
    }

    try {
      const response = await fetcher(buildApiUrl(baseUrl, path, query), {
        ...init,
        body,
        headers: requestHeaders,
        signal: init.signal ?? controller?.signal,
      });
      const payload = await readResponse(response);

      if (!response.ok) {
        throw new ApiError(`Request failed with status ${response.status}`, response.status, payload);
      }

      return payload as T;
    } finally {
      if (timeout !== undefined) {
        globalThis.clearTimeout(timeout);
      }
    }
  }

  return {
    delete: <T>(path: string, options?: ApiRequestOptions) =>
      request<T>(path, { ...options, method: "DELETE" }),
    get: <T>(path: string, options?: ApiRequestOptions) =>
      request<T>(path, { ...options, method: "GET" }),
    patch: <T>(path: string, json?: unknown, options?: ApiRequestOptions) =>
      request<T>(path, { ...options, json, method: "PATCH" }),
    post: <T>(path: string, json?: unknown, options?: ApiRequestOptions) =>
      request<T>(path, { ...options, json, method: "POST" }),
    put: <T>(path: string, json?: unknown, options?: ApiRequestOptions) =>
      request<T>(path, { ...options, json, method: "PUT" }),
  };
}

export const api = createApiClient();

export const newsletterApi = {
  create: (payload: NewsletterDraftInput) => api.post<NewsletterSummary>("/newsletters", payload),
  list: () => api.get<NewsletterSummary[]>("/newsletters"),
};
