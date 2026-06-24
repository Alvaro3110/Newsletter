export type NewsletterRunStatus = "success" | "running" | "failed" | "fallback";

export type NewsletterRun = {
  id: string;
  topic: string;
  status: NewsletterRunStatus;
  startedAt: string;
  durationMs: number;
  estimatedCostUsd: number;
  fallbackUsed: boolean;
};

export type DashboardMetrics = {
  totalRuns: number;
  successfulRuns: number;
  failedRuns: number;
  totalEstimatedCostUsd: number;
  averageDurationMs: number;
  fallbackRuns: number;
  successRate: number;
  fallbackRate: number;
};
