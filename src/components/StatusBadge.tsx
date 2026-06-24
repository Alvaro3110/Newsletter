import type { NewsletterRunStatus } from "../dashboard/types";

type StatusBadgeProps = {
  status: NewsletterRunStatus;
};

const labels: Record<NewsletterRunStatus, string> = {
  success: "Success",
  running: "Running",
  failed: "Failed",
  fallback: "Fallback",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      {labels[status]}
    </span>
  );
}
