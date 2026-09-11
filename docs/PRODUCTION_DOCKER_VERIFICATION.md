# Production Docker Verification

**Date:** 2026-09-11  
**Scope:** Same working backend image under real `ENVIRONMENT=production` runtime configuration  
**Not in scope:** Image rebuild, pest AI, frontend changes, HF architecture changes, production deploy

---

## Scorecard

| Check | Result |
|-------|--------|
| Docker image | **PASS** |
| Production startup | **PASS** |
| Production environment | **PASS** |
| MongoDB | **PASS** |
| Health | **PASS** |
| Sugarcane real HF | **PASS** |
| Rice real HF | **PASS** |
| Authentication | **PASS** |
| Authorization | **PASS** |
| Demo seed disabled | **PASS** |
| Mock AI disabled | **PASS** |
| CORS guards | **PASS** |
| Weak JWT guard | **PASS** |

---

## Image under test

| Field | Value |
|-------|--------|
| Repository:tag | `crop_project_sih-backend:latest` |
| Image ID | `e138b9dd15d9` |
| Size | ~10.5 GB |
| Container | `cropshield-backend-prod-verify` |
| Host port | `8006 → 8000` |
| Network | `crop_project_sih_default` |
| Mongo | existing `cropshield-mongodb` via `mongodb://mongodb:27017` |

**Note:** The previously long-running dev container (`cropshield-backend` on `:8005`) referenced image `513089aa022a`, whose layers are no longer fully present on disk (`docker commit` → digest not found). Verification used the tagged available image `crop_project_sih-backend:latest`, which contains a working ML stack (no rebuild performed in this step).

### Image ML stack (verified inside image)

```
torch 2.14.0+cu130
torchvision 0.29.0+cu130
transformers 5.17.0
AutoImageProcessor OK
```

Torch/torchvision versions were **not** changed.

---

## Production runtime configuration

Set only via container environment (JWT secret temporary, not printed, not committed, `.env` untouched):

| Variable | Value |
|----------|--------|
| `ENVIRONMENT` | `production` |
| `USE_MOCK_AI` | `false` |
| `ALLOW_DEMO_AUTH` | `false` |
| `SEED_DEMO_DATA` | `false` |
| `MONGO_URI` | `mongodb://mongodb:27017` |
| `CORS_ORIGINS` | explicit allowlist (`localhost:5173/5174`, `https://farmer.example.com`) |
| `JWT_SECRET` | strong temporary (≥32 chars, session-only) |

---

## VERIFIED

### Production startup

- Container started and stayed up.
- Log: `Production configuration validation passed.`
- Log: `Successfully connected to MongoDB: cropshield`
- Log: `Skipping demo seed: ENVIRONMENT=production`
- Log: `CropShield AI startup completed successfully.`
- No weak-secret failure, no wildcard CORS failure, no mock AI enabled.

### Health — `GET /api/v1/health`

- HTTP **200**
- `environment=production`
- `mongodb_connected=true`
- `persistence_mode=mongodb`
- `disease_inference=HUGGINGFACE_MULTI_MODEL`
- `seed_demo_data=false`
- `allow_demo_auth=false`
- Response did **not** expose JWT, Mongo URI, or API keys

### Sugarcane real HF (production Docker HTTP)

| Field | Value |
|-------|--------|
| HTTP | 200 / `completed` |
| Model | `LishaV01/agriculture-crop-disease-detection` |
| Raw label | `sugarcane_Healthy` |
| Display | Healthy Crop |
| Confidence | **0.955017** |
| Inference mode | `huggingface_trained` |
| Analysis ID | `an_9f1d840979` |
| Mongo document | present |
| Timing | ~74.4 s (cold model load) |

### Rice real HF (production Docker HTTP)

| Field | Value |
|-------|--------|
| HTTP | 200 / `completed` |
| Model | `wambugu71/crop_leaf_diseases_vit` |
| Raw label | `Rice___Brown_Spot` |
| Display | Brown Spot |
| Confidence | **0.23323** |
| Inference mode | `huggingface_trained` |
| Analysis ID | `an_184b23afcf` |
| Mongo document | present |
| Farmer history API | includes both analyses |
| Timing | ~12.9 s |

### Authentication / authorization

| Check | Result |
|-------|--------|
| Valid farmer JWT → `/auth/me` | **PASS** |
| Missing JWT → 401 | **PASS** |
| Invalid JWT → 401 | **PASS** |
| Farmer → `/admin/analytics` → 403 | **PASS** |
| Admin → `/admin/analytics` → 200 | **PASS** |

Farmer created via public `/auth/register` (production allows farmer self-register). Temporary admin inserted for authorization check only (`prod_verify_admin@example.com`); no demo seed accounts were created by production startup.

### Demo seed / mock AI

- Startup skipped demo seed (logged).
- Baseline before prod start: **3 users**, **0** `demo@` / `admin@cropshield.ai` accounts.
- After verification: **5 users** (registered farmer + temp admin from this test only), **0** demo seed emails, **21** analyses (prior 19 + Sugarcane + Rice).
- Prod container env: `USE_MOCK_AI=false`; inference mode `huggingface_trained` (not mock).

### CORS (live prod container)

- Allowed origin `http://localhost:5173` → `access-control-allow-origin: http://localhost:5173`
- Disallowed origin `https://evil.example.com` → **no** ACAO echo / no wildcard

### Production failure guards (isolated temporary containers)

| Test | Expected | Observed |
|------|----------|----------|
| A. `USE_MOCK_AI=true` | startup rejected | **PASS** — `CONFIGURATION ERROR: USE_MOCK_AI cannot be true...` / exit |
| B. `ALLOW_DEMO_AUTH=true` | startup rejected | **PASS** — SystemExit / startup failed |
| C. `SEED_DEMO_DATA=true` | startup rejected | **PASS** — SystemExit / startup failed |
| D. weak JWT (`short`) | startup rejected | **PASS** — SystemExit / startup failed |
| E. `CORS_ORIGINS=*` and empty CORS | startup rejected | **PASS** — both rejected |

Main production verify container configuration was **not** altered to make failure tests pass.

### Backend log scan (prod verify container)

- No torchvision operator/import errors
- No HF model load failures for Sugarcane/Rice
- No Mongo connection errors
- No mock disease AI usage
- No unhandled exceptions during diagnose
- Pest skip messages only (`USE_MOCK_PEST=false`) — expected

---

## BLOCKED

None for this production-configuration verification scope.

---

## NOT TESTED

- Full six-crop matrix under production (only Sugarcane + Rice, as required)
- Hosted deploy (Render/Vercel)
- Pest AI
- Frontend against production container
- Rootless container / HF cache volume persistence
- Changing torch/torchvision versions
- Long-running production hardening beyond startup guards

---

## Residual notes (non-blocking for this step)

1. Dev compose defaults still use `USE_MOCK_AI=true` / `SEED_DEMO_DATA=true` — must be overridden for any production-like compose run (guards will refuse if `ENVIRONMENT=production` with those flags).
2. Temporary verification users remain in Mongo (`prod_verify_farmer_*`, `prod_verify_admin@example.com`); they are not demo-seed accounts.
3. Temporary container `cropshield-backend-prod-verify` left running on `:8006` for inspection; stop/remove when no longer needed.
4. Prior dangling image id `513089aa022a` is incomplete on disk; prefer `crop_project_sih-backend:latest` (`e138b9dd15d9`) going forward.

---

## Files changed

- `docs/PRODUCTION_DOCKER_VERIFICATION.md` (this report)

No Dockerfile, requirements, backend code, or frontend changes in this step.
