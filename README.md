## Newsletter Dashboard

Operational dashboard for monitoring newsletter runs, status, cost, duration,
and fallback usage.

### Commands

```bash
npm install
npm run dev
npm test
npm run build
```

Open `http://localhost:5173/dashboard` after starting the dev server.

### Data Source

The dashboard uses mock data by default. To read from the prepared backend
adapter, set:

```bash
VITE_NEWSLETTER_RUNS_SOURCE=api
```

The adapter requests `GET /api/newsletter/runs` and accepts either an array of
runs or an object with `runs`, `data`, or `items`.
