import type { ReactNode } from "react";

type KpiTone =
  | "neutral"
  | "success"
  | "danger"
  | "cost"
  | "duration"
  | "fallback";

type KpiCardProps = {
  icon: ReactNode;
  title: string;
  value: string;
  helper: string;
  tone: KpiTone;
};

export function KpiCard({ icon, title, value, helper, tone }: KpiCardProps) {
  return (
    <article className={`kpi-card kpi-card--${tone}`}>
      <div className="kpi-card__topline">
        <span className="kpi-card__icon">{icon}</span>
        <h2>{title}</h2>
      </div>
      <strong>{value}</strong>
      <p>{helper}</p>
    </article>
  );
}
