import Link from "next/link";
import { Badge, Button } from "@/components/ui";

const secondaryNav = [
  { label: "Criacao", description: "Briefings" },
  { label: "Execucao", description: "Jobs" },
  { label: "Revisao", description: "Aprovacoes" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Navegacao principal">
        <Link href="/dashboard" className="sidebar__brand" aria-label="Ir para dashboard">
          <span className="sidebar__mark" aria-hidden="true">
            N
          </span>
          <span>
            <strong>Newsletter</strong>
            <span>MVP Console</span>
          </span>
        </Link>

        <nav className="sidebar__nav" aria-label="Secoes">
          <Link href="/dashboard" className="sidebar__nav-item sidebar__nav-item--active">
            <strong>Dashboard</strong>
            <span>Visao geral</span>
          </Link>
          {secondaryNav.map((item) => (
            <span key={item.label} className="sidebar__nav-item sidebar__nav-item--muted">
              <strong>{item.label}</strong>
              <span>{item.description}</span>
            </span>
          ))}
        </nav>

        <p className="sidebar__footer">
          Base pronta para conectar criacao, orquestracao, fallback e telemetria do produto.
        </p>
      </aside>

      <div className="main-shell">
        <header className="topbar">
          <div>
            <p className="topbar__eyebrow">Newsletter MVP</p>
            <h1>Console operacional</h1>
          </div>
          <div className="topbar__actions">
            <Badge tone="success">Base ativa</Badge>
            <Button type="button" size="sm">
              Novo briefing
            </Button>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
