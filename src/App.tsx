import {
  Activity,
  CircleCheck,
  CircleX,
  DollarSign,
  GitBranch,
  RefreshCcw,
  Timer,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { KpiCard } from "./components/KpiCard";
import { RecentRunsTable } from "./components/RecentRunsTable";
import { getDashboardMetrics } from "./dashboard/dashboardMetrics";
import {
  getNewsletterRuns,
  type NewsletterRunsError,
  type RunSource,
} from "./dashboard/newsletterRunsService";
import type { NewsletterRun } from "./dashboard/types";
import {
  formatCompactDuration,
  formatCurrency,
  formatInteger,
} from "./dashboard/valueFormatters";

type LoadState =
  | { status: "loading" }
  | { status: "ready"; runs: NewsletterRun[] }
  | { status: "error"; error: NewsletterRunsError | Error };

function getRunSourceFromUrl(): RunSource | undefined {
  const scenario = new URLSearchParams(window.location.search).get("scenario");

  if (
    scenario === "api" ||
    scenario === "empty" ||
    scenario === "error" ||
    scenario === "mock"
  ) {
    return scenario;
  }

  return undefined;
}

export function App() {
  const [loadState, setLoadState] = useState<LoadState>({ status: "loading" });

  const loadRuns = useCallback(() => {
    setLoadState({ status: "loading" });
    getNewsletterRuns({ source: getRunSourceFromUrl() })
      .then((runs) => setLoadState({ status: "ready", runs }))
      .catch((error: Error) => setLoadState({ status: "error", error }));
  }, []);

  useEffect(() => {
    loadRuns();
  }, [loadRuns]);

  const runs = loadState.status === "ready" ? loadState.runs : [];
  const metrics = useMemo(() => getDashboardMetrics(runs), [runs]);

  return (
    <main className="dashboard-shell">
      <section className="dashboard-header" aria-labelledby="dashboard-title">
        <div>
          <p className="eyebrow">Operacao newsletter</p>
          <h1 id="dashboard-title">Dashboard operacional</h1>
          <p className="header-copy">
            Execucoes recentes, custo estimado, tempo medio e fallback em uma
            visao consolidada.
          </p>
        </div>
        <div className="header-summary" aria-label="Resumo de execucoes">
          <span>{formatInteger(metrics.totalRuns)}</span>
          <small>execucoes monitoradas</small>
        </div>
      </section>

      {loadState.status === "error" ? (
        <section className="state-panel" role="alert">
          <div>
            <p className="eyebrow">Erro de carregamento</p>
            <h2>Dados indisponiveis</h2>
            <p>
              Nao foi possivel carregar as execucoes da newsletter neste
              momento.
            </p>
          </div>
          <button className="primary-button" type="button" onClick={loadRuns}>
            <RefreshCcw size={16} aria-hidden="true" />
            Tentar novamente
          </button>
        </section>
      ) : (
        <>
          <section className="kpi-grid" aria-label="Indicadores principais">
            <KpiCard
              icon={<Activity size={22} aria-hidden="true" />}
              title="Total de execucoes"
              value={formatInteger(metrics.totalRuns)}
              helper="Volume processado no periodo"
              tone="neutral"
            />
            <KpiCard
              icon={<CircleCheck size={22} aria-hidden="true" />}
              title="Execucoes com sucesso"
              value={formatInteger(metrics.successfulRuns)}
              helper={`${metrics.successRate}% de sucesso`}
              tone="success"
            />
            <KpiCard
              icon={<CircleX size={22} aria-hidden="true" />}
              title="Execucoes com erro"
              value={formatInteger(metrics.failedRuns)}
              helper="Falhas que exigem acompanhamento"
              tone="danger"
            />
            <KpiCard
              icon={<DollarSign size={22} aria-hidden="true" />}
              title="Custo total estimado"
              value={formatCurrency(metrics.totalEstimatedCostUsd)}
              helper="Soma dos custos reportados"
              tone="cost"
            />
            <KpiCard
              icon={<Timer size={22} aria-hidden="true" />}
              title="Tempo medio de execucao"
              value={formatCompactDuration(metrics.averageDurationMs)}
              helper="Media entre execucoes recentes"
              tone="duration"
            />
            <KpiCard
              icon={<GitBranch size={22} aria-hidden="true" />}
              title="Uso de fallback"
              value={formatInteger(metrics.fallbackRuns)}
              helper={`${metrics.fallbackRate}% das execucoes`}
              tone="fallback"
            />
          </section>

          {loadState.status === "loading" ? (
            <section className="state-panel" aria-live="polite">
              <div>
                <p className="eyebrow">Carregando</p>
                <h2>Buscando telemetria</h2>
                <p>Os indicadores serao atualizados quando os dados chegarem.</p>
              </div>
            </section>
          ) : (
            <RecentRunsTable runs={loadState.runs} />
          )}
        </>
      )}
    </main>
  );
}
