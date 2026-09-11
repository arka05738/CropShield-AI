# Production Security Audit

**Date:** 2026-09-11  
**Scope:** Configuration, production guards, secrets handling, CORS, Docker/Render/Vercel config, health/errors/uploads  
**Not in scope:** Git init, deploy, pest AI, frontend redesign, model architecture changes

Evidence: `docs/_pytest_prod_audit.log` (30 passed), isolated Docker prod containers on network `crop_project_sih_default`

---

## Configuration

**PASS** (with noted local risks)

| Setting | Expected production behavior | Status |
|---------|------------------------------|--------|
| `ENVIRONMENT` | `production` | Guarded |
| `USE_MOCK_AI` | must be `false` | Rejected if `true` |
| `ALLOW_DEMO_AUTH` | must be `false` | Rejected if `true` |
| `SEED_DEMO_DATA` | must be `false` | Rejected if `true`; seed also no-ops in production |
| `JWT_SECRET` | strong, ≥32 chars, not placeholder | Enforced |
| `CORS_ORIGINS` | explicit allowlist, no `*` | Enforced |
| `MONGO_URI` / `MONGO_DB_NAME` | runtime env (Render sync:false) | OK |
| `HF_MODEL_*` | public model IDs in config/Render | OK |
| `HF_TOKEN` | optional; not required for public models | OK |
| `PORT` | `${PORT:-8000}`, bind `0.0.0.0` | OK |

`.env` / `.env.example`: placeholders only in example; `.env` gitignored via `.gitignore`.

`docker-compose.yml` defaults `USE_MOCK_AI=true` and `SEED_DEMO_DATA=true` for **local development** — must never be used as a production deploy path without overrides.

---

## Production Guards

**PASS**

`validate_runtime_settings()` runs in FastAPI lifespan before serving traffic.

Verified by unit tests and Docker:

| Guard | Host unit test | Docker image test |
|-------|----------------|-------------------|
| Missing/weak/placeholder JWT | PASS | PASS (unit) |
| `USE_MOCK_AI=true` | PASS | PASS — container **exited** (`SystemExit`) |
| `SEED_DEMO_DATA=true` | PASS | (unit) |
| `ALLOW_DEMO_AUTH=true` | PASS | (unit) |
| Empty CORS / `*` stripped | PASS | (unit) |
| Valid production config | PASS | PASS — validation log + health |

Expanded forbidden JWT placeholders to include compose/test/example strings.

---

## Secrets

**PASS** (process) / **RISK** (local `.env`)

- No secrets copied into Docker image (`.dockerignore` excludes `.env`; image check: root/Backend `.env` absent).
- Health/API responses scrubbed in tests (no JWT/Mongo URI/API key material).
- Frontend uses only `VITE_API_BASE_URL` — no JWT/Mongo/HF/Groq secrets in client code.
- Render marks `JWT_SECRET`, `CORS_ORIGINS`, `MONGO_URI`, `GROQ_API_KEY` as `sync: false` (dashboard secrets).

**Rotation note:** A local root `.env` is used for development. If any live API keys (e.g. Groq) were ever shared outside the machine or pasted into chat/logs, **rotate those keys**. Values are not printed in this audit.

This workspace is **not** a git repository, so commit history of secrets cannot be audited here.

---

## CORS

**PASS**

- Parser strips `*`.
- Production with unset/empty origins → empty list → **startup fails closed**.
- Middleware: `allow_credentials=False`; explicit methods/headers.
- Development defaults remain localhost Vite ports only when `ENVIRONMENT!=production`.

---

## Docker Security

**PASS** (with residual risks)

| Check | Status |
|-------|--------|
| `.env` not in image | PASS |
| `.dockerignore` present | PASS |
| Secrets via runtime env | PASS |
| Bind `0.0.0.0` + `PORT` | PASS |
| Single exposed port 8000 | PASS |
| Runs as root | **RISK** (common for slim images; not changed to avoid breaking volume perms) |
| HF models not baked into image | PASS (lazy runtime download) |
| HF cache not persisted by volume | **RISK** (recreate loses cache) |
| Current image `513089aa022a` lacks `torchvision` | **RISK** — HF fails safe as `model_unavailable` until image rebuilt with Dockerfile torchvision step |

Dockerfile now installs `torchvision` in a separate pip step; that rebuild was **stopped** earlier — **baked image not yet updated**.

---

## HF Configuration

**PASS** (code/config) / **FAIL on pristine image without torchvision**

- Model IDs match verified registry (PlantVillage, LishaV01, wambugu71, Cotton, Sunflower).
- Lazy load + in-process cache; no hardcoded credentials.
- Failures → `model_unavailable`, `disease=null` (no heuristic disease).
- Host/real-compose path previously verified with torchvision present.
- Fresh production container from current image: Wheat diagnose → `model_unavailable` (missing torchvision).

---

## Health Endpoint

**PASS**

Exposes operational flags only (`persistence_mode`, `mongodb_connected`, disease mode labels, public model IDs, seed/demo flags forced false in production responses).

Does **not** expose JWT, Mongo URI, HF tokens, or API keys (asserted in tests).

---

## Error Handling

**PASS** (after minimal fix)

- Added global handler returning `{"detail":"Internal server error."}` without stack traces to clients (logs server-side).
- Upload/auth use explicit `HTTPException` messages without connection strings.
- OpenAPI `/docs` and `/redoc` **disabled when `ENVIRONMENT=production`** (source fix; present after next image rebuild).

---

## Upload Security

**PASS**

`StorageService` retains: extension allowlist, MIME check, size limit, magic bytes, PIL decode, path-safe filenames, upload dir containment. Not weakened.

---

## Render Configuration

**PASS** (configuration only — **NOT VERIFIED** as live deploy)

- Dockerfile: `infrastructure/Dockerfile.backend`
- Health: `/api/v1/health`
- `ENVIRONMENT=production`
- Mock/demo flags false
- HF model env vars set
- Secrets sync:false for JWT/CORS/Mongo/Groq
- PORT via container CMD

No live Render deployment claimed.

---

## Vercel Configuration

**PASS** (configuration)

- Farmer `Frontend SIH`: `VITE_API_BASE_URL || '/api/v1'`
- Admin: `getApiBase()` from `VITE_API_BASE_URL`
- `vercel.json` SPA rewrites only
- No backend secrets in frontend env contract

Production must set `VITE_API_BASE_URL` to the real API (not localhost). **NOT VERIFIED** as a live Vercel deploy.

---

## Production Docker Test

**PASS** (guards / mongo / auth / no demo seed)  
**FAIL** (real HF on pristine image without torchvision)

| Step | Result |
|------|--------|
| Invalid prod (`USE_MOCK_AI=true`) | **PASS** — startup refused, container exited |
| Valid prod start | **PASS** — `environment=production`, `mongodb_connected=true`, `seed_demo_data=false` |
| Demo seed skipped | **PASS** — log: Skipping demo seed |
| Register auth | **PASS** — HTTP 200 |
| Health secret scrub | **PASS** |
| Real HF diagnosis (Wheat) | **FAIL** — `model_unavailable` (image missing torchvision) |

---

## Remaining Risks

1. **Rebuild backend image** so torchvision is baked in (Dockerfile already updated; rebuild previously stopped).
2. **Rotate any live API keys** that may exist in local `.env` if they were ever exposed.
3. Container runs as **root**.
4. No persistent **HF cache volume** — cold starts re-download models after recreate.
5. `docker-compose.yml` defaults are **dev-oriented** (`USE_MOCK_AI=true`) — do not use as production compose without overrides.
6. Source fixes (docs disabled, root disease label, exception handler) require **image rebuild** to take effect in Docker.
7. No git history in this workspace — cannot prove secrets were never committed.
8. Render/Vercel **not deployed** in this audit.

---

## Fixes applied (minimal)

| File | Change |
|------|--------|
| `Backend/app/core/startup_checks.py` | Broader forbidden JWT placeholders |
| `Backend/app/main.py` | Prod docs off; accurate disease label; safe 500 handler |
| `Backend/tests/test_api.py` | Extra production guard + health secret tests |
| `infrastructure/Dockerfile.backend` | Separate `torchvision` install (pending image rebuild) |
| `.dockerignore` | Already present from prior step |

---

## Scorecard

| Area | Status |
|------|--------|
| Configuration | **PASS** |
| Production Guards | **PASS** |
| Secrets | **PASS** (rotate local keys if exposed) |
| CORS | **PASS** |
| Docker Security | **PASS** (with risks) |
| HF Configuration | **PASS** code / **FAIL** pristine image HF |
| Health Endpoint | **PASS** |
| Error Handling | **PASS** |
| Upload Security | **PASS** |
| Render Configuration | **PASS** (config) / deploy **NOT VERIFIED** |
| Vercel Configuration | **PASS** (config) / deploy **NOT VERIFIED** |
| Production Docker Test | **PASS** guards+mongo+auth; HF **FAIL** on current image |

**Verdict:** Production configuration guards are sound and fail closed. Do **not** claim production-ready deployment until the backend image is rebuilt with torchvision and hosting secrets/CORS are set on Render/Vercel.
