import { describe, expect, it } from "vitest";
import { getDashboardMetrics } from "./dashboardMetrics";
import type { NewsletterRun } from "./types";

const runs: NewsletterRun[] = [
  {
    id: "1",
    topic: "A",
    status: "success",
    startedAt: "2026-06-24T00:00:00.000Z",
    durationMs: 1000,
    estimatedCostUsd: 0.1,
    fallbackUsed: false,
  },
  {
    id: "2",
    topic: "B",
    status: "failed",
    startedAt: "2026-06-24T00:01:00.000Z",
    durationMs: 3000,
    estimatedCostUsd: 0.2,
    fallbackUsed: false,
  },
  {
    id: "3",
    topic: "C",
    status: "fallback",
    startedAt: "2026-06-24T00:02:00.000Z",
    durationMs: 5000,
    estimatedCostUsd: 0.3,
    fallbackUsed: true,
  },
];

describe("getDashboardMetrics", () => {
  it("calculates KPI totals and rates from newsletter runs", () => {
    expect(getDashboardMetrics(runs)).toEqual({
      totalRuns: 3,
      successfulRuns: 1,
      failedRuns: 1,
      totalEstimatedCostUsd: 0.6000000000000001,
      averageDurationMs: 3000,
      fallbackRuns: 1,
      successRate: 33,
      fallbackRate: 33,
    });
  });

  it("returns zeroed metrics for an empty dashboard", () => {
    expect(getDashboardMetrics([])).toEqual({
      totalRuns: 0,
      successfulRuns: 0,
      failedRuns: 0,
      totalEstimatedCostUsd: 0,
      averageDurationMs: 0,
      fallbackRuns: 0,
      successRate: 0,
      fallbackRate: 0,
    });
  });
});
