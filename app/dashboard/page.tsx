import { Badge, Button, Card, EmptyState, Input, StatusPill, Textarea } from "@/components/ui";
import { dashboardMetrics, newsletterPipeline, reviewQueue } from "@/lib/dashboard-data";

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <section className="dashboard__intro" aria-labelledby="dashboard-title">
        <div>
          <p className="dashboard__kicker">Visao macro</p>
          <h2 id="dashboard-title">Operacao de newsletters</h2>
          <p>
            Acompanhe briefings, execucoes automatizadas e revisoes editoriais em uma base
            preparada para integrar com o backend do MVP.
          </p>
        </div>
        <div className="dashboard__actions" aria-label="Acoes do dashboard">
          <Button type="button" variant="secondary">
            Revisar fila
          </Button>
          <Button type="button">Novo briefing</Button>
        </div>
      </section>

      <section className="metric-grid" aria-label="Indicadores principais">
        {dashboardMetrics.map((metric) => (
          <Card key={metric.label} className="metric-card">
            <div className="metric-card__meta">
              <span>{metric.label}</span>
              <Badge tone={metric.tone}>{metric.badge}</Badge>
            </div>
            <strong>{metric.value}</strong>
            <p>{metric.description}</p>
          </Card>
        ))}
      </section>

      <div className="dashboard__grid">
        <section className="dashboard__column" aria-labelledby="pipeline-title">
          <div className="section-heading">
            <div>
              <p className="section-heading__eyebrow">Pipeline</p>
              <h3 id="pipeline-title">Newsletters em andamento</h3>
            </div>
            <Badge tone="neutral">Hoje</Badge>
          </div>

          <div className="pipeline-list">
            {newsletterPipeline.map((newsletter) => (
              <Card key={newsletter.id} className="pipeline-card">
                <div className="pipeline-card__header">
                  <div>
                    <h4>{newsletter.title}</h4>
                    <p>{newsletter.audience}</p>
                  </div>
                  <StatusPill status={newsletter.status} />
                </div>
                <div className="pipeline-card__progress" aria-label={`${newsletter.progress}% concluido`}>
                  <span style={{ width: `${newsletter.progress}%` }} />
                </div>
                <div className="pipeline-card__footer">
                  <span>{newsletter.owner}</span>
                  <span>{newsletter.updatedAt}</span>
                </div>
              </Card>
            ))}
          </div>
        </section>

        <aside className="dashboard__column" aria-labelledby="briefing-title">
          <div className="section-heading">
            <div>
              <p className="section-heading__eyebrow">Criacao</p>
              <h3 id="briefing-title">Novo briefing</h3>
            </div>
            <Badge tone="info">Rascunho</Badge>
          </div>

          <Card className="briefing-card">
            <form className="briefing-form">
              <Input
                id="newsletter-title"
                label="Titulo"
                placeholder="Resumo semanal de produto"
                type="text"
              />
              <Input
                id="newsletter-audience"
                label="Publico"
                placeholder="Liderancas e operacoes"
                type="text"
              />
              <Textarea
                id="newsletter-context"
                label="Contexto"
                placeholder="Inclua objetivos, fontes e restricoes editoriais."
                rows={5}
              />
              <Button type="button" className="briefing-form__submit">
                Preparar rascunho
              </Button>
            </form>
          </Card>

          <div className="section-heading section-heading--compact">
            <div>
              <p className="section-heading__eyebrow">Revisao</p>
              <h3>Fila editorial</h3>
            </div>
          </div>

          {reviewQueue.length > 0 ? (
            <div className="review-list">
              {reviewQueue.map((item) => (
                <Card key={item.id} className="review-card">
                  <div>
                    <h4>{item.title}</h4>
                    <p>{item.note}</p>
                  </div>
                  <StatusPill status={item.status} />
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState
              title="Nenhuma revisao pendente"
              description="Quando a geracao enviar um rascunho para aprovacao, ele aparecera aqui."
              action={
                <Button type="button" variant="secondary">
                  Atualizar
                </Button>
              }
            />
          )}
        </aside>
      </div>
    </div>
  );
}
