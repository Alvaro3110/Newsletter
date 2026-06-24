import type { BadgeTone } from "@/components/ui";
import type { NewsletterSummary, ReviewQueueItem } from "@/types/newsletter";

export const dashboardMetrics: Array<{
  label: string;
  value: string;
  description: string;
  badge: string;
  tone: BadgeTone;
}> = [
  {
    label: "Newsletters ativas",
    value: "12",
    description: "Briefings em criacao, geracao ou revisao.",
    badge: "+3",
    tone: "success",
  },
  {
    label: "Tempo medio",
    value: "18m",
    description: "Da criacao do briefing ate o rascunho revisavel.",
    badge: "SLA",
    tone: "info",
  },
  {
    label: "Revisoes pendentes",
    value: "4",
    description: "Itens aguardando aprovacao editorial.",
    badge: "Hoje",
    tone: "warning",
  },
  {
    label: "Falhas tratadas",
    value: "2",
    description: "Execucoes cobertas por fallback operacional.",
    badge: "OK",
    tone: "neutral",
  },
];

export const newsletterPipeline: NewsletterSummary[] = [
  {
    id: "weekly-product",
    title: "Resumo semanal de produto",
    audience: "Liderancas, Produto e Operacoes",
    owner: "Equipe editorial",
    progress: 72,
    status: "review",
    updatedAt: "Atualizado ha 12 min",
  },
  {
    id: "market-pulse",
    title: "Pulso de mercado",
    audience: "Comercial e Customer Success",
    owner: "Automacao",
    progress: 46,
    status: "generating",
    updatedAt: "Execucao em andamento",
  },
  {
    id: "customer-digest",
    title: "Digest de clientes",
    audience: "Relacionamento e suporte",
    owner: "Operacoes",
    progress: 24,
    status: "queued",
    updatedAt: "Fila prioritaria",
  },
];

export const reviewQueue: ReviewQueueItem[] = [
  {
    id: "review-product",
    title: "Resumo semanal de produto",
    note: "Validar tom executivo e fontes antes do envio.",
    status: "review",
  },
  {
    id: "review-customers",
    title: "Digest de clientes",
    note: "Conferir segmentacao antes de agendar.",
    status: "scheduled",
  },
];
