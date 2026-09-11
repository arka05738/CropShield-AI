# Deployment Readiness Report — CropShield AI

**Verification date:** 2026-09-11  
**Scope:** Code-path inspection + executed tests/builds + live API checks  
**Rule:** Statuses below are evidence-based. Config files alone do not equal deployment readiness.

---

## Executive verdict

| Question | Answer |
|----------|--------|
| Is DenseNet121 implemented? | **No** — heuristic necrosis index only; **0** weight files (`.h5/.pt/.pth/.onnx`) in repo |
| Is pest detection production-real? | **No** — default returns `[]`; YOLO not used |
| Can the stack be demoed locally? | **Yes** (with `SEED_DEMO_DATA=true` in non-production) |
| Is it production-ready without further ops work? | **READY AFTER FIX** — authz/builds OK; Docker image build **not verified** (daemon down); secrets/ops checklist remains |

---

## Component matrix

| Component | Status | Evidence | Required Action |
|-----------|--------|----------|-----------------|
| **DenseNet121** | **NOT IMPLEMENTED** | No weight files; `disease_classifier.py` uses PIL resize 64×64 + necrotic pixel ratio; `inference_mode="heuristic"`; no `torch`, no `argmax`/`softmax` | Do not claim DenseNet in pitches; optionally add real weights later |
| **Crop detection** | **DEMO ONLY** (heuristic) | `crop_classifier.py` color-hash / `user_hint`; gatekeeper = ExG heuristic | Prefer farmer `crop_hint`; label as heuristic |
| **Disease detection** | **DEMO ONLY** (heuristic) | Taxonomy dict pick via necrosis ratio; confidence formula `0.85 + necrotic_ratio*0.5` — **not** model logits | Same as above |
| **Pest Detection** | **NOT IMPLEMENTED** (safe default) | `pest_detector.detect()` returns `[]` unless `USE_MOCK_PEST` or `PEST_MODEL_PATH`; live diagnose: `pests=0`, `pest_mode=unavailable`; `ultralytics` commented out of requirements | Keep `USE_MOCK_PEST=false` in prod |
| **RAG** | **READY AFTER FIX** / partial | ChromaDB + **64-dim hash** embedding (not MiniLM); curated `ICAR_POP_RECORDS`; advisory `_match_record` refuses cross-crop invent; optional Groq; assistant asks for crop if missing. Chroma fallback no longer defaults to Tomato (fixed this verification). Similarity thresholds: **none** (top-k only) | Document hash embeddings; rotate Groq key if `.env` was shared |
| **Weather** | **READY** (with caveats) | Open-Meteo via httpx; cache/`unavailable`/`mock` labeled; live health ran with `USE_MOCK_WEATHER=true` in verify session | Set `USE_MOCK_WEATHER=false` in prod; ensure egress |
| **GIS** | **DEMO ONLY** | Seeded hotspots + incremental case bump; admin-auth required (live 403 for farmer) | Do not claim live outbreak intelligence |
| **Expert Validation** | **READY** (memory/Mongo) | Request uses real analysis fields; review writes ground truth; expert roles required | Create real admin/expert users in prod |
| **Database** | **READY AFTER FIX** | Intended Mongo CRUD helpers exist; live verify: `persistence_mode=memory`, `mongodb_connected=false`. Admin analytics from `memory_store` counts (`is_demo_inflated=false`) | Provide durable `MONGO_URI` for prod |
| **Authentication** | **READY** | JWT + bcrypt; live login farmer/admin OK; unauth diagnose **401** | Set strong unique `JWT_SECRET` on Render |
| **Authorization** | **READY** | Live: FARMER → `/admin/analytics` → **403**; ADMIN → 200 | Keep role checks |
| **Farmer Frontend** | **READY AFTER FIX** | Separate SPA; no `components/admin`; build OK; `VITE_API_BASE_URL`; demo login stripped from **production dist** (grep: no `cropshield123`) | Set Vercel env `VITE_API_BASE_URL` |
| **Admin** | **READY AFTER FIX** | Independent `Admin/` app; same `/api/v1`; build OK; rejects FARMER at client+API | Set Vercel env; create admin user |
| **Render** | **READY AFTER FIX** | Dockerfile uses `${PORT:-8000}`; `render.yaml` present; **Docker image build NOT executed** — Docker Desktop engine not running on verifier host | Start Docker / build on CI or Render; set secrets |
| **Vercel** | **READY AFTER FIX** | `vercel.json` SPA rewrites present; API base via env; localhost only in Vite **dev** proxy | Deploy with prod API URL + CORS |

Status legend: **READY** | **READY AFTER FIX** | **NOT READY** | **NOT IMPLEMENTED** | **DEMO ONLY**

---

## 1. AI implementation (traced)

### Path (actual)

```
Frontend FormData upload
  → POST /api/v1/diagnose (analysis.py) [JWT required]
  → storage_service.save_image (PIL verify)
  → gatekeeper.inspect (ExG heuristic)
  → crop_classifier.identify (hint or color-hash heuristic)
  → disease_model.inference (necrosis heuristic)  ||  pest_detector.detect (empty by default)
  → weather_service.get_weather
  → risk_engine.calculate_risk (rules)
  → advisory_engine.generate_advisory (curated match / unavailable)
  → persist_analysis → AnalysisResponse + inference_meta
```

### DenseNet121 checklist

| Question | Answer |
|----------|--------|
| Real DenseNet121 exists? | **No** |
| Model weights on disk? | **None** (glob `*.h5/*.pt/*.pth/*.onnx` = 0) |
| Formats used? | N/A |
| Loaded during inference? | **No** |
| Preprocessing? | Resize to 64×64 RGB NumPy only |
| argmax? | **No** — integer index from necrosis formula |
| Disease classes from model metadata? | Hardcoded `CROP_DISEASE_TAXONOMY` dict |
| Confidence from model output? | **No** — hand-tuned float |
| Crop detection? | Heuristic / user hint |
| Disease detection? | Heuristic |

Live diagnose sample: `disease.inference_mode=heuristic`, `pest_inference_mode=unavailable`, `pests=0`.

---

## 2. Pest detection

| Question | Answer |
|----------|--------|
| Real pest model present? | **No** |
| YOLO installed & used? | **Not** in active requirements; optional import only if `PEST_MODEL_PATH` set; even then `_detect_yolo` returns `[]` |
| Bounding boxes real? | Only if `USE_MOCK_PEST=true` (fixed fake boxes, `is_mock=True`) |
| Production default | Empty list — **verified live** |

---

## 3. RAG

```
query (crop + disease [+ pest])
  → FastAgriculturalEmbedding (64-dim token hash)
  → Chroma collection agriculture_knowledge (n_results default 2)
  → advisory _match_record(crop, disease) OR unavailable advisory
  → optional Groq (doses forced from matched record)
```

| Item | Actual |
|------|--------|
| Embedding | Hash 64-d — **not** MiniLM/sentence-transformers |
| Vector store | Chroma persistent |
| Retrieval count | `n_results=2` |
| Relevance threshold | **None** (no min similarity gate) |
| Knowledge | Curated Python `ICAR_POP_RECORDS` (+ markdown in `knowledge-base/` not auto-ingested as PDFs) |
| LLM | Groq if `GROQ_API_KEY` set |
| No-fabricate | Advisory unavailable path; assistant refuses inventing doses when no retrieval |

---

## 4. Database

| Entity | Persistence |
|--------|-------------|
| users | `memory_store` + optional Mongo upsert |
| analyses / history | same |
| validations | same |
| recommendations | embedded in analysis `advisory` |
| farms | key exists; often empty |
| Admin analytics | Computed from store lists — live: `inflated=False`, `analyses=3` from seed in **dev** |

**Live verify:** Mongo unreachable → `persistence_mode=memory` (non-durable).

---

## 5. Authorization (executed)

| Case | Result |
|------|--------|
| FARMER login | 200, role FARMER |
| ADMIN login | 200, role ADMIN |
| FARMER → `GET /api/v1/admin/analytics` | **403** |
| ADMIN → analytics | **200** |
| Unauthenticated diagnose | **401** |

---

## 6. Admin separation

| Check | Result |
|-------|--------|
| `Frontend SIH/src/components/admin` | **Absent** (0 files) |
| `Admin/` independent Vite app | **Yes** |
| Shared backend | **Yes** `/api/v1` |
| Duplicated backend logic in Admin | **No** |

---

## 7. Production configuration scan

| Finding | Severity |
|---------|----------|
| Root `.env` contains live `GROQ_API_KEY` and weak `JWT_SECRET` | **CRITICAL** if committed/shared — rotate key; keep `.env` gitignored |
| `localhost` / `127.0.0.1` in Vite **dev** proxies | OK for local only |
| docker-compose defaults `localhost` API for frontend build args | Local compose only |
| Production apps use `VITE_API_BASE_URL` | Code present |
| CORS no longer `*` | OK; must set Vercel origins on Render |
| Demo passwords in **source** under `import.meta.env.DEV` guards | Production **dist** has **no** `cropshield123` (verified by grep) |

---

## 8. Demo credentials (safety fix applied this verification)

**Before:** `seed_initial_data()` always seeded `demo@` / `admin@` with `cropshield123` on every startup (including production risk).

**After (safety fix):**
- Blocked when `ENVIRONMENT=production` (verified: 0 users seeded)
- Requires `SEED_DEMO_DATA=true` otherwise
- `render.yaml` sets `SEED_DEMO_DATA=false`
- Production frontend/admin builds do not embed demo password strings
- README no longer publishes demo password as production practice

**Still present for local/tests:** password strings in `seed_data.py`, tests, and DEV-only UI paths — acceptable for SIH local demos when explicitly seeded.

---

## 9. Builds / tests executed

| Command | Result |
|---------|--------|
| `pytest Backend/tests/test_api.py -v` | **11 passed** |
| `Frontend SIH` `npm run build` | **exit 0** |
| `Admin` `npm run build` | **exit 0** |
| `uvicorn` startup + `/api/v1/health` | **healthy** |
| Live auth + diagnose + history + admin 403 | **Verified** |
| `docker build` backend | **FAILED** — Docker engine not running (`dockerDesktopLinuxEngine` pipe missing) |

---

## 10. What is genuinely working

- FastAPI health, JWT auth, role authorization
- Image upload validation + gatekeeper reject path
- Heuristic crop/disease pipeline with honest `inference_meta`
- Empty pest list in default production config
- Weather client with labeled fallbacks
- Curated RAG match / unavailable guidance path
- History persistence (memory or Mongo)
- Expert validation queue APIs
- Separate farmer & admin SPAs + production builds
- Admin analytics from real store counts (not inflated)

## 11. What is only heuristic/demo

- Crop ID, disease ID, gatekeeper
- GIS hotspot seeds
- Demo users/analyses when `SEED_DEMO_DATA=true`
- Mock pest when explicitly enabled
- Hash embeddings

## 12. What is missing

- Trained DenseNet121 / YOLO weights and loaders that run argmax on real logits
- MiniLM (or equivalent) embeddings + relevance threshold
- Verified Docker image build on this machine
- Durable Mongo in the live verification environment
- Voice; full i18n UI

## 13. What is unsafe / must fix before public deploy

1. Ensure Render: `ENVIRONMENT=production`, `SEED_DEMO_DATA=false`, `ALLOW_DEMO_AUTH=false`, strong `JWT_SECRET`
2. Rotate any exposed Groq API key from local `.env` if the file was shared
3. Provision real admin user (no known public password)
4. Set `CORS_ORIGINS` to exact Vercel domains
5. Set `VITE_API_BASE_URL` on both Vercel projects
6. Attach Mongo (or accept ephemeral memory)
7. Confirm Docker/Render build succeeds in CI or Render dashboard
8. Never claim DenseNet121 / YOLO production accuracy

## 14. Render readiness

**READY AFTER FIX** — Dockerfile/`PORT`/health/render.yaml are structurally correct; **image build was not verified** here because Docker Desktop engine was down.

## 15. Vercel readiness

**READY AFTER FIX** — builds succeed; SPA rewrites exist; must configure `VITE_API_BASE_URL` and backend CORS. Not deployed in this verification.

---

## Exact remaining commands

```bash
# Local backend (dev seed optional)
cd Backend
set SEED_DEMO_DATA=true
set ENVIRONMENT=development
set JWT_SECRET=your-local-secret
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Tests
pytest tests/test_api.py -v

# Frontends
cd "Frontend SIH" && npm run build
cd ../Admin && npm run build

# Docker (when Desktop engine is running)
docker build -f infrastructure/Dockerfile.backend -t cropshield-backend .
docker run --rm -e PORT=8000 -e JWT_SECRET=... -e ENVIRONMENT=production -e SEED_DEMO_DATA=false -p 8000:8000 cropshield-backend
curl http://127.0.0.1:8000/api/v1/health
```

## Exact files needing attention before deploy

| File | Why |
|------|-----|
| Root `.env` | Live secrets; never commit; rotate Groq/JWT |
| `Backend/app/ml/disease_classifier.py` | Heuristic only — marketing claims |
| `Backend/app/ml/pest_detector.py` | No real YOLO |
| `Backend/app/rag/chroma_service.py` | Hash embeddings |
| `infrastructure/Dockerfile.backend` | Build not verified on this host |
| `infrastructure/render/render.yaml` | Must set sync:false secrets in Render UI |
| Vercel project env | `VITE_API_BASE_URL` |
| `Backend/app/services/seed_data.py` | Demo passwords remain for explicit non-prod seed |

---

## Inference path evidence (filenames are not enough)

- Disease: `Backend/app/ml/disease_classifier.py` lines using `necrotic_ratio` / taxonomy index — not DenseNet.
- Pest: `Backend/app/ml/pest_detector.py` returns `[]` when `USE_MOCK_PEST=false`.
- Weights search: **zero** model binary files in repository.
