import { describe, expect, it, vi } from "vitest";
import {
  NewsletterRunsError,
  getNewsletterRuns,
  normalizeRunsResponse,
} from "./newsletterRunsService";

describe("normalizeRunsResponse", () => {
  it("accepts backend response aliases prepared for telemetry data", () => {
    expect(
      normalizeRunsResponse({
        runs: [
          {
            run_id: "abc",
            tema: "Monitoramento",
            status: "completed",
            timestamp: "2026-06-24T04:00:00.000Z",
            duration_seconds: 42,
            cost: "0.25",
            fallback_used: true,
          },
        ],
      }),
    ).toEqual([
      {
        id: "abc",
        topic: "Monitoramento",
        status: "fallback",
        startedAt: "2026-06-24T04:00:00.000Z",
        durationMs: 42000,
        estimatedCostUsd: 0.25,
        fallbackUsed: true,
      },
    ]);
  });

  it("returns an empty array when the payload has no runs collection", () => {
    expect(normalizeRunsResponse({ total: 0 })).toEqual([]);
  });
});

describe("getNewsletterRuns", () => {
  it("uses the configured endpoint when source is api", async () => {
    const fetcher = vi.fn(async () => {
      return new Response(
        JSON.stringify({
          runs: [{ id: "1", topic: "Teste", status: "success" }],
        }),
        { status: 200 },
      );
    });

    const runs = await getNewsletterRuns({
      source: "api",
      endpoint: "/api/newsletter/runs",
      fetcher,
    });

    expect(fetcher).toHaveBeenCalledWith("/api/newsletter/runs", {
      headers: { Accept: "application/json" },
    });
    expect(runs[0]).toMatchObject({
      id: "1",
      topic: "Teste",
      status: "success",
    });
  });

  it("throws a domain error when the API request fails", async () => {
    const fetcher = vi.fn(async () => new Response(null, { status: 500 }));

    await expect(
      getNewsletterRuns({ source: "api", fetcher }),
    ).rejects.toBeInstanceOf(NewsletterRunsError);
  });
});
