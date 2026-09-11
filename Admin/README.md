# CropShield Admin

Independent admin console (Vite + React + TypeScript + Tailwind).

## Local development

```bash
npm install
npm run dev
```

Dev server proxies `/api` and `/uploads` to the local backend (see `vite.config.ts`).

## Environment

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Production API base including `/api/v1`. Required on Vercel. Empty in local dev uses relative `/api/v1` via Vite proxy. |

## Auth

Only `ADMIN`, `SUPER_ADMIN`, `EXPERT`, and `EXTENSION_WORKER` may sign in. Farmer accounts are rejected by the Admin client **and** by backend role checks.

Local demo accounts exist **only** when the backend is run with `SEED_DEMO_DATA=true` and `ENVIRONMENT` is **not** `production`. Do not enable demo seeding on Render.

## Deploy (Vercel)

1. Import the `Admin/` directory as a Vite project.
2. Set `VITE_API_BASE_URL=https://<your-backend>/api/v1`
3. Ensure `vercel.json` SPA rewrites are present (already included).
4. Add the Vercel origin to backend `CORS_ORIGINS`.
