# Production Environment Variable Checklist

**Date:** 2026-09-11  
**Scope:** Deployment preparation only (no secrets committed).

## Architecture (target)

| Tier | Host | Artifact |
|------|------|----------|
| Farmer SPA | Vercel | `Frontend SIH/` (+ `vercel.json` SPA rewrites) |
| Admin SPA | Vercel | `Admin/` (+ `vercel.json` SPA rewrites) |
| FastAPI backend | Render (Docker) | `infrastructure/Dockerfile.backend` + `infrastructure/render/render.yaml` |
| Database | Managed MongoDB Atlas (or equivalent) | `MONGO_URI` / `MONGO_DB_NAME=cropshield` |

---

## Backend (Render) — required

| Variable | Production value | Notes |
|----------|------------------|-------|
| `ENVIRONMENT` | `production` | Startup fails closed without strong JWT + explicit CORS |
| `USE_MOCK_AI` | `false` | Real HF disease path only |
| `USE_MOCK_PEST` | `false` | Real YOLO path only |
| `USE_MOCK_WEATHER` | `false` | |
| `ALLOW_DEMO_AUTH` | `false` | Production startup **rejects** if true |
| `SEED_DEMO_DATA` | `false` | Production startup **rejects** if true |
| `JWT_SECRET` | **strong runtime secret** (≥32 chars, not a placeholder) | Set in Render dashboard; never commit |
| `CORS_ORIGINS` | Explicit Farmer + Admin Vercel HTTPS origins (CSV) | **No `*`** |
| `MONGO_URI` | Managed MongoDB connection string | Set in Render dashboard; never commit |
| `MONGO_DB_NAME` | `cropshield` | |
| `PORT` | Injected by Render | Dockerfile binds `0.0.0.0:${PORT:-8000}` |

## Backend — disease HF models (must remain correct)

| Variable | Value |
|----------|-------|
| `USE_HF_DISEASE_MODEL` | `true` |
| `HF_MODEL_PLANTVILLAGE` | `kimcomehome/plantvillage-vit-leaf-disease` |
| `HF_MODEL_SUGARCANE` | `LishaV01/agriculture-crop-disease-detection` |
| `HF_MODEL_RICE` | `wambugu71/crop_leaf_diseases_vit` |
| `HF_MODEL_WHEAT` | `wambugu71/crop_leaf_diseases_vit` |
| `HF_MODEL_COTTON` | `YaswanthReddy23/ViT_Cotton` |
| `HF_MODEL_SUNFLOWER` | `YaswanthReddy23/ViT_Sunflower` |
| `HF_DISEASE_MODEL_ID` | `kimcomehome/plantvillage-vit-leaf-disease` |

## Backend — pest HF model

| Variable | Value |
|----------|-------|
| `USE_PEST_HF_MODEL` | `true` |
| `PEST_HF_MODEL_ID` | `underdogquality/yolo11s-pest-detection` |
| `PEST_CONFIDENCE_THRESHOLD` | `0.25` |

## Backend — optional / recommended

| Variable | Notes |
|----------|-------|
| `HF_TOKEN` | Hub rate limits / gated models; set in Render secrets |
| `GROQ_API_KEY` | Optional LLM assist; set in Render secrets |
| `GROQ_MODEL` | Default `llama-3.3-70b-versatile` |
| `CHROMA_PERSIST_DIR` | `/app/Backend/data/chroma` (ephemeral on free tier unless disk attached) |
| `UPLOAD_DIR` | `/app/Backend/uploads` |
| `MAX_UPLOAD_BYTES` | Default 10 MB |

## Farmer (Vercel) — public build-time only

| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | `https://<render-backend-host>/api/v1` |

**Do not** put `JWT_SECRET`, `MONGO_URI`, `HF_TOKEN`, or `GROQ_API_KEY` in Farmer env.

## Admin (Vercel) — public build-time only

| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | `https://<render-backend-host>/api/v1` |

**Do not** put backend secrets in Admin env.

## Health expectations (after deploy)

`GET https://<render-host>/api/v1/health` → **HTTP 200**

Must show (labels vary by payload shape):

- `ENVIRONMENT` / production indicators as designed
- Mongo connected when `MONGO_URI` is valid
- Disease / pest inference modes **not** mock
- **No** JWT secrets, Mongo credentials, API keys, or password hashes in the response
