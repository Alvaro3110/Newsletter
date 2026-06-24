# Newsletter

Aplicação Next.js para criar e iniciar execuções do pipeline de newsletter.

## Desenvolvimento

```bash
npm install
npm run dev
```

A tela principal fica em `/newsletter/new`.

## Backend

O formulário envia para `POST /api/newsletter/run`. Em desenvolvimento, a rota
retorna uma resposta local. Para encaminhar para o backend real, configure uma
das variáveis:

- `NEWSLETTER_RUN_ENDPOINT`: URL completa do endpoint de execução.
- `NEWSLETTER_BACKEND_URL`: base URL do backend; a rota usará
  `/api/newsletter/run`.
