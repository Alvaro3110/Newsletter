import type { NewsletterRun } from "./types";

export const mockNewsletterRuns: NewsletterRun[] = [
  {
    id: "run-2026-06-24-001",
    topic: "IA aplicada a produtividade",
    status: "success",
    startedAt: "2026-06-24T03:42:00.000Z",
    durationMs: 188000,
    estimatedCostUsd: 0.42,
    fallbackUsed: false,
  },
  {
    id: "run-2026-06-24-002",
    topic: "Mercado cripto semanal",
    status: "running",
    startedAt: "2026-06-24T04:05:00.000Z",
    durationMs: 72000,
    estimatedCostUsd: 0.18,
    fallbackUsed: false,
  },
  {
    id: "run-2026-06-23-003",
    topic: "Tendencias em SaaS B2B",
    status: "fallback",
    startedAt: "2026-06-23T22:18:00.000Z",
    durationMs: 264000,
    estimatedCostUsd: 0.57,
    fallbackUsed: true,
  },
  {
    id: "run-2026-06-23-004",
    topic: "Resumo de seguranca digital",
    status: "failed",
    startedAt: "2026-06-23T18:36:00.000Z",
    durationMs: 91000,
    estimatedCostUsd: 0.11,
    fallbackUsed: false,
  },
  {
    id: "run-2026-06-22-005",
    topic: "Educacao e ferramentas de IA",
    status: "success",
    startedAt: "2026-06-22T15:10:00.000Z",
    durationMs: 211000,
    estimatedCostUsd: 0.36,
    fallbackUsed: false,
  },
];
