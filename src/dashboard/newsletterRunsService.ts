import { mockNewsletterRuns } from "./mockRuns";
import type { NewsletterRun, NewsletterRunStatus } from "./types";

export type RunSource = "mock" | "api" | "empty" | "error";

type FetchLike = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Response>;

type GetNewsletterRunsOptions = {
  source?: RunSource;
  endpoint?: string;
  fetcher?: FetchLike;
};

const DEFAULT_ENDPOINT = "/api/newsletter/runs";

export class NewsletterRunsError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NewsletterRunsError";
  }
}

export async function getNewsletterRuns({
  source = getDefaultRunSource(),
  endpoint = DEFAULT_ENDPOINT,
  fetcher = fetch,
}: GetNewsletterRunsOptions = {}): Promise<NewsletterRun[]> {
  if (source === "mock") {
    return mockNewsletterRuns;
  }

  if (source === "empty") {
    return [];
  }

  if (source === "error") {
    throw new NewsletterRunsError("Forced newsletter runs loading error.");
  }

  const response = await fetcher(endpoint, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new NewsletterRunsError(
      `Newsletter runs request failed with status ${response.status}.`,
    );
  }

  return normalizeRunsResponse(await response.json());
}

export function normalizeRunsResponse(payload: unknown): NewsletterRun[] {
  const rawRuns = Array.isArray(payload)
    ? payload
    : getArrayValue(asRecord(payload), ["runs", "data", "items"]);

  return rawRuns.map(normalizeRun);
}

function normalizeRun(rawRun: unknown, index: number): NewsletterRun {
  const record = asRecord(rawRun);
  const fallbackUsed = toBoolean(
    getValue(record, ["fallbackUsed", "fallback_used", "fallback"]),
  );
  const status = normalizeStatus(
    toStringValue(getValue(record, ["status", "state"])),
    fallbackUsed,
  );

  return {
    id:
      toStringValue(getValue(record, ["id", "runId", "run_id"])) ??
      `newsletter-run-${index + 1}`,
    topic:
      toStringValue(
        getValue(record, ["topic", "theme", "tema", "newsletterTopic"]),
      ) ?? "Tema nao informado",
    status,
    startedAt:
      toStringValue(
        getValue(record, ["startedAt", "createdAt", "timestamp", "datetime"]),
      ) ?? new Date(0).toISOString(),
    durationMs: toDurationMs(
      getValue(record, [
        "durationMs",
        "duration_ms",
        "duration",
        "durationSeconds",
        "duration_seconds",
      ]),
    ),
    estimatedCostUsd: toNumber(
      getValue(record, [
        "estimatedCostUsd",
        "estimated_cost_usd",
        "costUsd",
        "cost_usd",
        "cost",
      ]),
    ),
    fallbackUsed,
  };
}

function getDefaultRunSource(): RunSource {
  return import.meta.env.VITE_NEWSLETTER_RUNS_SOURCE === "api" ? "api" : "mock";
}

function normalizeStatus(
  status: string | undefined,
  fallbackUsed: boolean,
): NewsletterRunStatus {
  const normalized = status?.toLowerCase().replace(/\s+/g, "_");

  if (normalized === "running" || normalized === "in_progress") {
    return "running";
  }

  if (
    normalized === "failed" ||
    normalized === "failure" ||
    normalized === "error"
  ) {
    return "failed";
  }

  if (normalized === "fallback" || normalized === "degraded") {
    return "fallback";
  }

  if (
    normalized === "success" ||
    normalized === "succeeded" ||
    normalized === "completed" ||
    normalized === "complete" ||
    normalized === "ok"
  ) {
    return fallbackUsed ? "fallback" : "success";
  }

  return fallbackUsed ? "fallback" : "success";
}

function asRecord(value: unknown): Record<string, unknown> {
  if (typeof value === "object" && value !== null && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }

  return {};
}

function getArrayValue(
  record: Record<string, unknown>,
  keys: string[],
): unknown[] {
  for (const key of keys) {
    const value = record[key];
    if (Array.isArray(value)) {
      return value;
    }
  }

  return [];
}

function getValue(record: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    if (record[key] !== undefined && record[key] !== null) {
      return record[key];
    }
  }

  return undefined;
}

function toStringValue(value: unknown) {
  return typeof value === "string" && value.trim().length > 0
    ? value
    : undefined;
}

function toNumber(value: unknown) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string" && value.trim().length > 0) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  return 0;
}

function toDurationMs(value: unknown) {
  const numericValue = toNumber(value);
  return numericValue > 0 && numericValue < 1000
    ? numericValue * 1000
    : numericValue;
}

function toBoolean(value: unknown) {
  if (typeof value === "boolean") {
    return value;
  }

  if (typeof value === "string") {
    return ["true", "yes", "sim", "1"].includes(value.toLowerCase());
  }

  if (typeof value === "number") {
    return value === 1;
  }

  return false;
}
