import { EmptyState } from "./EmptyState";
import { StatusBadge } from "./StatusBadge";
import type { NewsletterRun } from "../dashboard/types";
import {
  formatCurrency,
  formatDateTime,
  formatDuration,
} from "../dashboard/valueFormatters";

type RecentRunsTableProps = {
  runs: NewsletterRun[];
};

export function RecentRunsTable({ runs }: RecentRunsTableProps) {
  if (runs.length === 0) {
    return <EmptyState />;
  }

  return (
    <section className="runs-panel" aria-labelledby="recent-runs-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Historico</p>
          <h2 id="recent-runs-title">Execucoes recentes</h2>
        </div>
        <span>{runs.length} registros</span>
      </div>

      <div className="runs-table-wrap">
        <table className="runs-table">
          <thead>
            <tr>
              <th scope="col">Tema</th>
              <th scope="col">Status</th>
              <th scope="col">Data/hora</th>
              <th scope="col">Duracao</th>
              <th scope="col">Custo</th>
              <th scope="col">Fallback usado</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id}>
                <td data-label="Tema">
                  <span className="topic-cell">{run.topic}</span>
                </td>
                <td data-label="Status">
                  <StatusBadge status={run.status} />
                </td>
                <td data-label="Data/hora">{formatDateTime(run.startedAt)}</td>
                <td data-label="Duracao">{formatDuration(run.durationMs)}</td>
                <td data-label="Custo">
                  {formatCurrency(run.estimatedCostUsd)}
                </td>
                <td data-label="Fallback usado">
                  {run.fallbackUsed ? "Sim" : "Nao"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
