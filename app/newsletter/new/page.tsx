"use client";

import { FormEvent, useMemo, useState } from "react";
import styles from "./page.module.css";

type NewsletterForm = {
  theme: string;
  audience: string;
  tone: string;
  topicCount: number;
  notes: string;
};

type RunResponse = {
  run_id: string;
  status: string;
  message: string;
};

const initialForm: NewsletterForm = {
  theme: "",
  audience: "",
  tone: "informativo",
  topicCount: 5,
  notes: ""
};

const toneOptions = [
  { value: "informativo", label: "Informativo" },
  { value: "analitico", label: "Analítico" },
  { value: "executivo", label: "Executivo" },
  { value: "conversacional", label: "Conversacional" }
];

export default function NewNewsletterPage() {
  const [form, setForm] = useState<NewsletterForm>(initialForm);
  const [fieldError, setFieldError] = useState("");
  const [apiError, setApiError] = useState("");
  const [result, setResult] = useState<RunResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const trimmedTheme = form.theme.trim();
  const canSubmit = useMemo(() => !isLoading, [isLoading]);

  function updateForm<K extends keyof NewsletterForm>(
    field: K,
    value: NewsletterForm[K]
  ) {
    setForm((current) => ({ ...current, [field]: value }));

    if (field === "theme" && String(value).trim()) {
      setFieldError("");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!trimmedTheme) {
      setFieldError("Informe o tema da newsletter para iniciar a geração.");
      setResult(null);
      return;
    }

    setIsLoading(true);
    setApiError("");
    setFieldError("");
    setResult(null);

    try {
      const response = await fetch("/api/newsletter/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          theme: trimmedTheme,
          audience: form.audience.trim(),
          tone: form.tone,
          topic_count: form.topicCount,
          notes: form.notes.trim()
        })
      });

      const payload = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          payload?.message ??
            "Não foi possível iniciar a newsletter agora. Tente novamente."
        );
      }

      setResult({
        run_id: String(payload?.run_id ?? ""),
        status: String(payload?.status ?? "recebido"),
        message:
          String(payload?.message ?? "") ||
          "Execução iniciada. Acompanhe o processamento pelo identificador."
      });
    } catch (error) {
      setApiError(
        error instanceof Error
          ? error.message
          : "Não foi possível iniciar a newsletter agora. Tente novamente."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className={styles.page}>
      <section className={styles.header}>
        <p className={styles.kicker}>Newsletter</p>
        <div>
          <h1>Nova newsletter</h1>
          <p>Configure a execução editorial e acompanhe o retorno inicial.</p>
        </div>
      </section>

      <section className={styles.workspace} aria-label="Criação de newsletter">
        <form className={styles.formPanel} onSubmit={handleSubmit} noValidate>
          <div className={styles.formGrid}>
            <label className={styles.field}>
              <span>Tema da newsletter</span>
              <input
                aria-describedby={fieldError ? "theme-error" : undefined}
                aria-invalid={fieldError ? "true" : "false"}
                autoComplete="off"
                name="theme"
                onChange={(event) => updateForm("theme", event.target.value)}
                placeholder="Ex.: tendências de IA para pequenas empresas"
                value={form.theme}
              />
            </label>

            <label className={styles.field}>
              <span>Público-alvo</span>
              <input
                autoComplete="off"
                name="audience"
                onChange={(event) =>
                  updateForm("audience", event.target.value)
                }
                placeholder="Ex.: fundadores e líderes de produto"
                value={form.audience}
              />
            </label>

            <label className={styles.field}>
              <span>Tom editorial</span>
              <select
                name="tone"
                onChange={(event) => updateForm("tone", event.target.value)}
                value={form.tone}
              >
                {toneOptions.map((tone) => (
                  <option key={tone.value} value={tone.value}>
                    {tone.label}
                  </option>
                ))}
              </select>
            </label>

            <label className={styles.field}>
              <span>Quantidade de tópicos</span>
              <input
                max={12}
                min={1}
                name="topicCount"
                onChange={(event) =>
                  updateForm(
                    "topicCount",
                    Number.parseInt(event.target.value, 10) || 1
                  )
                }
                type="number"
                value={form.topicCount}
              />
            </label>

            <label className={`${styles.field} ${styles.fullWidth}`}>
              <span>Observações adicionais</span>
              <textarea
                name="notes"
                onChange={(event) => updateForm("notes", event.target.value)}
                placeholder="Contexto, restrições, fontes ou preferências editoriais"
                rows={5}
                value={form.notes}
              />
            </label>
          </div>

          {fieldError ? (
            <p className={styles.validationMessage} id="theme-error" role="alert">
              {fieldError}
            </p>
          ) : null}

          <div className={styles.actions}>
            <button
              className={styles.primaryButton}
              disabled={!canSubmit}
              type="submit"
            >
              {isLoading ? "Gerando..." : "Gerar Newsletter"}
            </button>
          </div>
        </form>

        <aside className={styles.resultPanel} aria-live="polite">
          <div className={styles.resultHeader}>
            <span className={styles.statusDot} aria-hidden="true" />
            <h2>Execução</h2>
          </div>

          {isLoading ? (
            <div className={styles.loadingState} role="status">
              <span className={styles.spinner} aria-hidden="true" />
              <p>Pipeline em execução...</p>
            </div>
          ) : null}

          {apiError ? (
            <div className={styles.errorState} role="alert">
              <strong>Falha ao iniciar</strong>
              <p>{apiError}</p>
            </div>
          ) : null}

          {result ? (
            <div className={styles.successState}>
              <dl>
                <div>
                  <dt>run_id</dt>
                  <dd>{result.run_id}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>{result.status}</dd>
                </div>
                <div>
                  <dt>Mensagem</dt>
                  <dd>{result.message}</dd>
                </div>
              </dl>
            </div>
          ) : null}

          {!isLoading && !apiError && !result ? (
            <p className={styles.emptyState}>
              O retorno da execução aparecerá aqui.
            </p>
          ) : null}
        </aside>
      </section>
    </main>
  );
}
