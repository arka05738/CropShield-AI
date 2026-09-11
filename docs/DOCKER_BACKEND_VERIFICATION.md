# Docker Backend Verification

**Date:** 2026-09-11  
**Host API under test:** `http://127.0.0.1:8005/api/v1`  
**(Host `:8000` occupied by unrelated `cropcare-backend`; temporary compose port override used — in-container still binds `0.0.0.0:8000` / `PORT`.)**

Evidence: `docs/_docker_build.log`, `docs/_docker_hf_results.json`, `docs/_docker_restart_authz.json`

---

## Docker Engine

**PASS**

---

## Backend Build

**PASS** (initial image)

| Metric | Value |
|--------|-------|
| Image | `crop_project_sih-backend:latest` |
| Size | **10.4 GB** |
| Build time | **~1602 s** (~26.7 min) |
| Warnings | Compose `version` obsolete; pip root-user notice; large CUDA/torch wheels |

**Follow-up image rebuild with torchvision:** first attempt **FAIL** (pip hash mismatch when torchvision added to the same `requirements.txt` install). Dockerfile updated to install `torchvision` in a **separate** pip step; rebuild status recorded at end of verification session.

**Genuine bug fixed:** container HF inference required `torchvision` (transformers `AutoImageProcessor`). Missing from image → `model_unavailable` with null disease (safe fail). Runtime install + Dockerfile/requirements documentation fix applied.

---

## MongoDB Container

**PASS** — `cropshield-mongodb` (`mongo:7.0`), volume `mongo_data` retained

---

## Backend Container

**PASS** — `cropshield-backend`, `USE_MOCK_AI=false`, `MONGO_URI=mongodb://mongodb:27017`

---

## Health Endpoint

**PASS**

`GET http://127.0.0.1:8005/api/v1/health` → HTTP 200  
`persistence_mode=mongodb`, `mongodb_connected=true`, `disease_inference=HUGGINGFACE_MULTI_MODEL`

---

## Backend → MongoDB

**PASS**

Architecture confirmed: FastAPI → `mongodb:27017` → MongoDB container (not `localhost` inside Docker).

---

## Real HF Disease Inference

**PASS** (after torchvision available in container)

---

## Six Crop Tests

| Crop | Model ID | Disease | Confidence | HTTP | Total ms |
|------|----------|---------|------------|------|----------|
| Grape | kimcomehome/plantvillage-vit-leaf-disease | Esca (Black Measles) | 0.0215 | 200 | 116547 |
| Sugarcane | LishaV01/agriculture-crop-disease-detection | Healthy Crop | 0.7781 | 200 | 10485 |
| Rice | wambugu71/crop_leaf_diseases_vit | Brown Spot | 0.7357 | 200 | 9668 |
| Wheat | wambugu71/crop_leaf_diseases_vit | Healthy Crop | 0.0309 | 200 | 235 |
| Cotton | YaswanthReddy23/ViT_Cotton | Leaf Hopper Jassids | 0.2963 | 200 | 73733 |
| Sunflower | YaswanthReddy23/ViT_Sunflower | Gray mold | 0.3662 | 200 | 103105 |

All `inference_mode=huggingface_trained`, correct registry routing. Synthetic leaf images — not field accuracy claims.

---

## Unsupported Crop

**PASS** — Millet → `model_unavailable`, `disease=null`, `confidence=null`

---

## RAG

**PASS**

- Disease miss (e.g. Grape Esca, Rice Brown Spot): `guidance_available=false`, empty dose, no fabricated treatment  
- Healthy path (Sugarcane/Wheat): monitoring guidance, not disease-KB dosage invention  

---

## Mongo Persistence

**PASS** — diagnoses written; history lists records before restart

---

## Restart Persistence

**PASS** — `docker restart cropshield-backend` only; Mongo volume kept  
Analysis `an_6d7debb457` still GET 200 + in farmer history after restart

---

## Farmer Authorization

**PASS** — owner 200; other farmer **403**

---

## Admin Authorization

**PASS** — admin cases includes persisted diagnosis

---

## Security

**PASS** (with notes)

| Check | Result |
|-------|--------|
| `.env` in image | **Absent** (`ROOT_ENV_ABSENT`, `BACKEND_ENV_ABSENT`) |
| Dockerfile COPY scope | `Backend/` + `knowledge-base/` only |
| `.dockerignore` | **Added** (excludes `.env`, frontends, docs noise) |
| Secrets in image layers | No `.env` copied; JWT/GROQ injected at **runtime** via compose |
| Bind address | `uvicorn --host 0.0.0.0 --port ${PORT:-8000}` |

Compose default `USE_MOCK_AI=true` must be overridden for real HF (`USE_MOCK_AI=false` used here).

---

## HF Cache

| Topic | Detail |
|-------|--------|
| At image build | **Not** pre-downloaded (`HF_CACHE_EMPTY_AT_IMAGE_BUILD`) |
| At runtime | Downloaded on first inference into `/root/.cache/huggingface` (~**1.1 GB** after six models) |
| After `docker restart` | Cache on container writable layer **survives**; Wheat reload ~4 s vs first ~80 s |
| After `docker compose up --force-recreate` | Cache **lost** unless a HF cache volume is added (not redesigned here) |

---

## Local Docker Performance

**LOCAL DOCKER PERFORMANCE** (not Render numbers)

| Metric | Approx. |
|--------|---------|
| Image build | ~1602 s |
| Backend ready after restart | ~18–33 s to healthy |
| Health (host) | typically &lt;1 s |
| First Grape HF (cold download+load) | ~117 s |
| Warm Wheat (after restart, disk cache) | ~46 s first post-restart load / prior warm ~0.2 s in-process |

---

## Render Implications

- Dockerfile already uses `PORT` + `0.0.0.0` (Render-compatible).  
- Image ~10 GB with full CUDA torch wheels — cold starts and registry push will be heavy on free/low tiers.  
- HF models download at runtime; without a persistent HF cache volume, each new instance redownloads.  
- Must set runtime secrets (`JWT_SECRET`, `CORS_ORIGINS`, `MONGO_URI`); production Dockerfile defaults already `USE_MOCK_AI=false`.  
- Ensure deployed image includes **torchvision** (Dockerfile separate install step).

---

## Remaining Issues

1. **Image rebuild with torchvision into published tag:** first pip-hash failure; Dockerfile separate-step fix applied — confirm rebuild completes before relying on a fresh `compose up --build` without runtime pip.  
2. **No HF cache volume** in compose — recreate loses ~1.1 GB model cache.  
3. **Default compose `USE_MOCK_AI=true`** — easy to accidentally test mocks if env not overridden.  
4. **Host port 8000 conflict** with unrelated container — verification used `:8005` override file.  
5. **Compose `version` key obsolete** warning (harmless).  
6. **Not production-ready** — large image, runtime model download, torchvision bake-in must be confirmed on clean rebuild.

---

## Scorecard

| Area | Status |
|------|--------|
| Docker Engine | PASS |
| Backend Build | PASS |
| MongoDB Container | PASS |
| Backend Container | PASS |
| Health Endpoint | PASS |
| Backend → MongoDB | PASS |
| Real HF Disease Inference | PASS |
| Six Crop Tests | PASS |
| Unsupported Crop | PASS |
| RAG | PASS |
| Mongo Persistence | PASS |
| Restart Persistence | PASS |
| Farmer Authorization | PASS |
| Admin Authorization | PASS |
| Security | PASS |

**Production readiness: not claimed.**
