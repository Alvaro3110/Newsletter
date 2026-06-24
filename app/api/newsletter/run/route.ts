import { NextRequest, NextResponse } from "next/server";

type NewsletterRunPayload = {
  theme?: unknown;
  audience?: unknown;
  tone?: unknown;
  topic_count?: unknown;
  notes?: unknown;
};

type NewsletterRunResponse = {
  run_id: string;
  status: string;
  message: string;
};

function isString(value: unknown): value is string {
  return typeof value === "string";
}

function normalizedTopicCount(value: unknown) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return 5;
  }

  return Math.min(Math.max(Math.trunc(value), 1), 12);
}

function makeRunId(theme: string) {
  const slug = theme
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")
    .slice(0, 32);

  return `local-${slug || "newsletter"}-${Date.now()}`;
}

function resolveBackendEndpoint() {
  if (process.env.NEWSLETTER_RUN_ENDPOINT) {
    return process.env.NEWSLETTER_RUN_ENDPOINT;
  }

  if (!process.env.NEWSLETTER_BACKEND_URL) {
    return "";
  }

  try {
    return new URL(
      "/api/newsletter/run",
      process.env.NEWSLETTER_BACKEND_URL
    ).toString();
  } catch {
    return "invalid-backend-url";
  }
}

async function parseJsonResponse(response: Response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as Partial<NewsletterRunResponse> & {
      message?: string;
    };
  } catch {
    return {
      message: text
    };
  }
}

export async function POST(request: NextRequest) {
  const payload = (await request.json().catch(() => null)) as
    | NewsletterRunPayload
    | null;

  const theme = isString(payload?.theme) ? payload.theme.trim() : "";

  if (!theme) {
    return NextResponse.json(
      {
        message: "Informe o tema da newsletter antes de iniciar a execução."
      },
      { status: 400 }
    );
  }

  const requestBody = {
    theme,
    audience: isString(payload?.audience) ? payload.audience.trim() : "",
    tone: isString(payload?.tone) ? payload.tone : "informativo",
    topic_count: normalizedTopicCount(payload?.topic_count),
    notes: isString(payload?.notes) ? payload.notes.trim() : ""
  };

  const endpoint = resolveBackendEndpoint();

  if (endpoint) {
    if (endpoint === "invalid-backend-url") {
      return NextResponse.json(
        {
          message:
            "A URL do backend de newsletters está inválida. Revise a configuração e tente novamente."
        },
        { status: 500 }
      );
    }

    try {
      const backendResponse = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
      });

      const backendPayload = await parseJsonResponse(backendResponse);

      if (!backendResponse.ok) {
        return NextResponse.json(
          {
            message:
              backendPayload?.message ??
              "O backend não conseguiu iniciar a newsletter."
          },
          { status: backendResponse.status }
        );
      }

      return NextResponse.json(
        {
          run_id: String(backendPayload?.run_id ?? makeRunId(theme)),
          status: String(backendPayload?.status ?? "received"),
          message:
            String(backendPayload?.message ?? "") ||
            "Execução encaminhada para o backend."
        },
        { status: backendResponse.status === 204 ? 202 : backendResponse.status }
      );
    } catch {
      return NextResponse.json(
        {
          message:
            "Não foi possível conectar ao backend de newsletters. Tente novamente em instantes."
        },
        { status: 502 }
      );
    }
  }

  return NextResponse.json(
    {
      run_id: makeRunId(theme),
      status: "queued",
      message:
        "Execução registrada localmente. Configure NEWSLETTER_RUN_ENDPOINT para usar o backend real."
    },
    { status: 202 }
  );
}
