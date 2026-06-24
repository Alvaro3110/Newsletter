import type { DashboardMetrics, NewsletterRun } from "./types";

export function getDashboardMetrics(runs: NewsletterRun[]): DashboardMetrics {
  const totalRuns = runs.length;
  const successfulRuns = runs.filter((run) => run.status === "success").length;
  const failedRuns = runs.filter((run) => run.status === "failed").length;
  const fallbackRuns = runs.filter(
    (run) => run.fallbackUsed || run.status === "fallback",
  ).length;
  const totalDurationMs = runs.reduce((sum, run) => sum + run.durationMs, 0);
  const totalEstimatedCostUsd = runs.reduce(
    (sum, run) => sum + run.estimatedCostUsd,
    0,
  );

  return {
    totalRuns,
    successfulRuns,
    failedRuns,
    totalEstimatedCostUsd,
    averageDurationMs: totalRuns === 0 ? 0 : totalDurationMs / totalRuns,
    fallbackRuns,
    successRate: toRate(successfulRuns, totalRuns),
    fallbackRate: toRate(fallbackRuns, totalRuns),
  };
}

function toRate(value: number, total: number) {
  return total === 0 ? 0 : Math.round((value / total) * 100);
}
