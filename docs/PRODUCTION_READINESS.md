# Production Readiness — CropShield AI

**Updated:** 2026-09-11  
**Scope:** Production-readiness hardening only (no new AI features).

## Status table

| Component | Status | Evidence | Remaining Action |
|-----------|--------|----------|------------------|
| Authentication | READY AFTER CONFIGURATION | JWT + bcrypt; production startup **fails** without strong `JWT_SECRET` (≥32, not placeholder) | Set `JWT_SECRET` on Render |
| Authorization | READY | Admin routes use `require_role`; farmer→admin returns 403 (pytest) | Keep roles on all new admin routes |
| Database | READY AFTER CONFIGURATION | Mongo via `MONGO_URI` when reachable; else labelled `persistence_mode=memory` on `/health` | Provide durable Mongo for prod |
| Disease inference | DEMO ONLY | Heuristic necrosis taxonomy; health reports `DEMO_HEURISTIC`; no DenseNet weights | Do not claim DenseNet121 |
| Pest inference | NOT IMPLEMENTED | Default empty; health `UNAVAILABLE`; `USE_MOCK_PEST` must stay false in prod | Keep unavailable unless real weights |
| RAG | READY AFTER CONFIGURATION | Chroma + hash embeddings; no-match → guidance unavailable; no fabricated dosages on miss | Optional Groq key; document hash embeddings |
| Weather | READY AFTER CONFIGURATION | Open-Meteo; cache/unavailable/mock labeled | Set `USE_MOCK_WEATHER=false` |
| GIS | DEMO ONLY | Seeded + recorded cases; admin-auth required | Do not claim live outbreak feeds |
| Validation | READY | Expert roles; ground truth stored; no auto-retrain | Create real expert/admin users |
| Farmer frontend | READY AFTER CONFIGURATION | Vite build; `VITE_API_BASE_URL`; SPA `vercel.json`; demo login DEV-only | Set Vercel env |
| Admin frontend | READY AFTER CONFIGURATION | Independent app; build; SPA rewrites; FARMER rejected client+server | Set Vercel env |
| Backend | READY AFTER CONFIGURATION | FastAPI; startup validation; `/api/v1/health` unauthenticated | Configure Render env |
| Docker | NOT READY | Dockerfile present (`PORT`, `0.0.0.0`, prod flags). **Docker build not verified** — Docker Desktop engine unavailable on verification host | Start Docker Desktop and run `docker build -f infrastructure/Dockerfile.backend -t cropshield-backend .` |
| Render | READY AFTER CONFIGURATION | `render.yaml` + Dockerfile; health `/api/v1/health`; `SEED_DEMO_DATA=false` | Set secrets: JWT, CORS, optional Mongo/Groq |
| Vercel Farmer | READY AFTER CONFIGURATION | `Frontend SIH/vercel.json`; relative API default | Set `VITE_API_BASE_URL` |
| Vercel Admin | READY AFTER CONFIGURATION | `Admin/vercel.json`; same API contract | Set `VITE_API_BASE_URL` |
| Security | READY AFTER CONFIGURATION | Demo seed blocked in production; CORS allowlist; upload validation; `.env` gitignored | Rotate any leaked Groq/JWT; never commit `.env` |

## Persistence limitation

If MongoDB is unreachable, the API continues with an **in-memory** store. Data is **lost on restart**. `/api/v1/health` reports `persistence_mode` and `mongodb_connected` so operators are not misled.

## AI honesty

- Disease/crop: **DEMO / HEURISTIC**
- Pest: **UNAVAILABLE** unless a real model path is configured (not shipped)
- Do not market DenseNet121 or YOLO as operational for this repository state

## Manual configuration checklist

1. Render: `JWT_SECRET`, `CORS_ORIGINS` (Vercel URLs), `ENVIRONMENT=production`
2. Render: `SEED_DEMO_DATA=false`, `ALLOW_DEMO_AUTH=false`
3. Optional: `MONGO_URI`, `GROQ_API_KEY`
4. Vercel Farmer + Admin: `VITE_API_BASE_URL=https://<render-host>/api/v1`
5. Create a real admin account without public demo passwords
