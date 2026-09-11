# Docker Compose Reconciliation

**Date:** 2026-09-11  
**Step:** 11 — Reconcile stale compose backend with current verified source  
**Scope:** Backend image rebuild + auth compatibility only (no frontend, no deploy, no Git)

---

## Scorecard

| Item | Result |
|------|--------|
| 1. Old compose image | **PASS** (identified & replaced) |
| 2. New image ID | **PASS** |
| 3. Source/image reconciliation | **PASS** |
| 4. Pest API status (`:8005`) | **PASS** |
| 5. Disease API status | **PASS** |
| 6. MongoDB status | **PASS** |
| 7. Development seed configuration | **PASS** (explicit) |
| 8. Password-hash mismatch root cause | **PASS** (explained + demo hash refresh) |
| 9. Auth regression | **PASS** |
| 10. Backend tests | **PASS** *(host pest real-smoke still skipped — not converted to PASS)* |
| 11. Docker pest test | **PASS** (`REAL MODEL EXECUTED — ZERO DETECTIONS`) |
| 12. Remaining issues | See below |

---

## 1. Old compose image

| Field | Value |
|-------|--------|
| Container | `cropshield-backend` on host `:8005` |
| Old image digest / ID | `sha256:513089aa022a…` (`513089aa022a`) |
| Problem | Pre-pest source; no `/api/v1/pests/*`; no `ultralytics`; `pest_inference=UNAVAILABLE` |
| Action | Stopped + removed container (**MongoDB volume preserved**) |

Verified newer image that previously had pest weights (`e138b9dd15d9`) was **not** reused as the final compose image — compose was rebuilt from **current source**.

---

## 2. New image ID

| Field | Value |
|-------|--------|
| Tag | `crop_project_sih-backend:latest` |
| Image ID | `753c8f04be2f` |
| Manifest | `sha256:753c8f04be2fa85df179acdf294f0870ecc3e30ed10e35581da94070bb8c8021` |
| Size | ~11.1 GB |
| Contains | Current `Backend/` + `ultralytics` 8.4.146 + pest package |

---

## 3. Source / image reconciliation

- Build: `docker compose build backend` from `infrastructure/Dockerfile.backend` + current repo `Backend/`.
- Run: `docker compose up -d backend`
- `docker compose ps`: `cropshield-backend` Up, `8005→8000`; `cropshield-mongodb` Up (unchanged volume).
- Health after start:
  - `disease_inference=HUGGINGFACE_MULTI_MODEL`
  - `pest_inference=HUGGINGFACE_YOLO`
  - `pest_model_id=underdogquality/yolo11s-pest-detection`
  - `mongodb_connected=true`
  - `persistence_mode=mongodb`

---

## 4. Pest API status — PASS

`POST /api/v1/pests/detect` on `:8005` (authenticated farmer):

| Field | Value |
|-------|--------|
| HTTP | 200 |
| Endpoint | Exists (no 404) |
| Model | `underdogquality/yolo11s-pest-detection` |
| Status | `no_pest_detected` |
| Count | 0 |
| Severity | `none` |
| Timing | ~29.7 s LOCAL |
| Outcome | **REAL MODEL EXECUTED — ZERO DETECTIONS** |
| History | `GET /pests/history` count=1 |
| Mongo | `pest_analyses=1` |

Not mock. Zero detections on synthetic leaf is valid smoke evidence (not pest-free).

---

## 5. Disease API status — PASS

Representative rebuild check:

| Field | Value |
|-------|--------|
| Crop | Sugarcane |
| HTTP | 200 |
| Status | `completed` |
| Model | `LishaV01/agriculture-crop-disease-detection` |
| Disease (AI) | Healthy Crop |
| AI confidence | 0.065 |
| Timing | ~81.6 s LOCAL (cold load) |

Disease path remains intact after pest-capable rebuild.

---

## 6. MongoDB status — PASS

- URI: `mongodb://mongodb:27017` (compose service DNS)
- Mode: `mongodb` (not memory-only)
- Volume `mongo_data` **not deleted**
- After reconcile tests (approx.): `analyses=30`, `pest_analyses=1`, `users=10`

---

## 7. Development seed configuration — PASS

`docker-compose.yml` is explicitly a **local DEVELOPMENT** profile:

| Variable | Compose value | Intent |
|----------|---------------|--------|
| `ENVIRONMENT` | `development` | Local only |
| `USE_MOCK_AI` | `false` | Real HF disease |
| `USE_MOCK_PEST` | `false` | Real YOLO pest |
| `USE_PEST_HF_MODEL` | `true` | Enable pest HF |
| `ALLOW_DEMO_AUTH` | `false` | No soft auth |
| `SEED_DEMO_DATA` | `true` | **Intentional local demo accounts** |

Production configuration remains separate. Production-verify `:8006` still reports:

- `ENVIRONMENT=production`
- `SEED_DEMO_DATA=false`
- `ALLOW_DEMO_AUTH=false`

(when that container remains up). Production startup still fails closed if seed/demo-auth are enabled.

Host port mapping is now explicit: **`8005:8000`** (host `:8000` occupied by unrelated `cropcare-backend`).

---

## 8. Password-hash mismatch — root cause

**Classification: A (stale image code) + B (stale demo user hashes not refreshed on re-seed)**  
**Not C (algorithm change in current code)** — current register/login both use the same bcrypt helpers.  
**Not D (application bug in hash/verify)** — round-trip works.

### Findings

- Current code: `get_password_hash` / `verify_password` via `bcrypt` only (`Backend/app/core/security.py`).
- Seed previously **inserted** demo users only if missing; it did **not** refresh hashes for already-persisted Mongo demo users after auth/image upgrades.
- Old compose image (`513089aa022a`) could not run current pest/auth paths consistently with users registered under the newer code path (and vice versa).

### Minimum fix (development only)

When `SEED_DEMO_DATA=true` and `ENVIRONMENT≠production`, seed now refreshes **known demo account** password hashes and persists them (`seed_data.py`). Non-demo accounts are untouched.

Regression tests added: `Backend/tests/test_password_hash.py`.

**No passwords or hashes printed in this report.**

---

## 9. Auth regression — PASS

On rebuilt `:8005`:

| Check | Result |
|-------|--------|
| `demo@cropshield.ai` login | PASS (FARMER) |
| Invalid password | 401 |
| Farmer → `/admin/analytics` | 403 |
| `admin@cropshield.ai` → `/admin/analytics` | 200 |
| Newly registered farmer login | PASS |

---

## 10. Backend tests

Host:

```
python -m pytest tests -v
```

Result: **38 passed, 1 skipped** (~104s).  
Skipped: `test_pest_real_smoke` (host lacks ultralytics) — **not** reported as PASS.  
New: `test_password_hash.py` (2 passed).

Docker pest inference is reported separately in §11.

---

## 11. Docker pest test — PASS

See §4. Real YOLO11s inference executed in compose backend; zero detections on synthetic leaf.

---

## 12. Remaining issues

1. Host pest real-smoke still skipped without local `ultralytics` (Docker path is the verified real-pest path).
2. Frontend still not re-validated end-to-end in this step (explicitly deferred).
3. Production deploy still not done (by design).
4. Temporary containers from earlier validation (`cropshield-backend-prod-verify` on `:8006`) may still exist alongside compose; they are outside the reconciled compose service.

---

## Files changed

| File | Change |
|------|--------|
| `docker-compose.yml` | Explicit dev env, port `8005`, pest/HF flags, seed documented |
| `Backend/app/services/seed_data.py` | Refresh demo password hashes under SEED_DEMO_DATA |
| `Backend/tests/test_password_hash.py` | Auth bcrypt regression tests |
| `docs/DOCKER_COMPOSE_RECONCILIATION.md` | This report |
