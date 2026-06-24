import type { NewsletterStatus } from "@/types/newsletter";
import { cn } from "@/lib/class-names";

const statusLabels: Record<NewsletterStatus, string> = {
  approved: "Aprovada",
  draft: "Rascunho",
  failed: "Falha",
  generating: "Gerando",
  queued: "Na fila",
  review: "Em revisao",
  scheduled: "Agendada",
  sent: "Enviada",
};

export function StatusPill({ status }: { status: NewsletterStatus }) {
  return <span className={cn("status-pill", `status-pill--${status}`)}>{statusLabels[status]}</span>;
}
