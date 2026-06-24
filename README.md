# Newsletter Frontend

Base frontend em Next.js para criacao, acompanhamento e revisao de newsletters do MVP.

## Stack

- Next.js App Router
- TypeScript
- CSS global com variaveis de tema
- Componentes reutilizaveis em `components/ui`

## Requisitos

- Node.js 22 ou superior
- npm 10 ou superior

## Executar localmente

Instale as dependencias:

```bash
npm install
```

Inicie o servidor de desenvolvimento:

```bash
npm run dev
```

Acesse:

```text
http://localhost:3000/dashboard
```

## Scripts

```bash
npm run dev
npm run lint
npm run build
npm run start
```

## Estrutura

- `app`: rotas App Router, layout raiz e pagina `/dashboard`.
- `components`: layout e componentes base do design system.
- `lib`: utilitarios e dados estaticos usados pela interface.
- `services`: cliente HTTP preparado para integracao com o backend.
- `types`: tipos compartilhados do dominio de newsletters.

## Backend API

Defina `NEXT_PUBLIC_API_BASE_URL` para apontar o cliente HTTP para o backend quando a API estiver disponivel:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```
