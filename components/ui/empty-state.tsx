import type { ReactNode } from "react";

export type EmptyStateProps = {
  title: string;
  description: string;
  action?: ReactNode;
};

export function EmptyState({ action, description, title }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state__content">
        <h3>{title}</h3>
        <p>{description}</p>
        {action}
      </div>
    </div>
  );
}
