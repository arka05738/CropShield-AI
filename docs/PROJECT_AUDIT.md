# CropShield AI — Project Audit Report

**Problem Statement ID:** 26131 — Early Detection and Management of Crop Diseases and Pest Infestations  
**Smart India Hackathon:** 2026  
**Audit date:** 2026-09-11  
**Scope:** Full recursive inspection of `crop_Project_SIH` (Admin/, Frontend SIH/, Backend/, infrastructure/, knowledge-base/, config, tests, docs)  
**Rule:** Source code is the source of truth. README marketing claims that contradict code are flagged as gaps, not as implemented features.

---

## 1. Current Architecture

```
crop_Project_SIH/
├── Admin/                    # EMPTY placeholder (0 source files)
├── Frontend SIH/             # Vite + React 19 + TS + Tailwind 4 (farmer + admin UI combined)
├── Backend/                  # FastAPI app under Backend/app/
├── infrastructure/           # Dockerfiles (path names mismatch repo folders)
├── knowledge-base/           # Single ICAR POP markdown master file
├── docker-compose.yml
├── .env / .env.example
└── README.md                 # Overclaims capabilities vs actual code
```

| Layer | Technology (actual) | Notes |
|-------|---------------------|-------|
| Farmer + Admin UI | Single SPA, local `useState` tabs | No React Router |
| API | FastAPI, dual mount `/api/v1` + root | OpenAPI at `/docs`, `/redoc` |
| Auth | JWT (PyJWT) + bcrypt | Soft auth: missing token → demo farmer |
| Persistence | In-memory `memory_store` | Mongo connect/indexes exist; **no CRUD** |
| Vector store | ChromaDB + 64-dim hash embeddings | Not sentence-transformers |
| LLM | Optional Groq | Fallback to curated ICAR dict / templates |
| Weather | Open-Meteo via httpx | Mock fallback when offline |
| Vision | Pillow + NumPy heuristics | **No trained weight files on disk** |

---

## 2. Current Working Features

### Backend (functional as demo services)
- Health / root info endpoints
- Register / login / JWT issue
- Image upload to local disk with size/extension checks
- Crop gatekeeper (ExG chlorophyll heuristic) — rejects blank/non-green images
- Heuristic crop ID, disease ID, pest bbox generation
- Deterministic risk fusion (disease + pest + weather rules)
- Open-Meteo weather fetch + 1h cache + agro risk flags
- Chroma seed/query with hash embeddings + ICAR curated records
- Groq-backed advisory/assistant when `GROQ_API_KEY` is set
- Validation queue request/review (in-memory)
- GIS hotspot GeoJSON (seeded + incremental cluster bump)
- Admin analytics / models / users / cases endpoints (mostly open)
- Pytest suite covering health, login, gatekeeper reject, diagnose, GIS, admin stats, assistant

### Frontend SIH (functional UI wired to APIs)
- Login / register modal + demo account shortcuts
- Farmer dashboard, analyze upload/camera, report view, history, AI assistant chat
- Leaflet admin GIS map consuming hotspots API
- Admin analytics charts (Recharts), validation queue, knowledge manager, model registry UI
- Dosage calculator scales backend dose × tank volume
- Pest canvas overlay from API bbox list
- Vite dev proxy `/api` → `127.0.0.1:8000`

---

## 3. Missing Features (vs SIH target / README)

| Feature | Status |
|---------|--------|
| Separate Admin application under `Admin/` | Missing (folder empty) |
| React Router farmer/admin routes | Missing |
| DenseNet121 crop-specific models (Sugarcane/Grapes/Sunflower/Cotton) | **Not in codebase**; no `.h5/.pt/.pth/.onnx` |
| Real YOLO pest detector | Missing (heuristic mock only) |
| MongoDB persistence for users/analyses | Missing (connect-only) |
| Real sentence-transformer embeddings | Missing (hash embedding) |
| Role-enforced admin APIs | Missing (`require_role` unused) |
| Multilingual UI (11 languages) | Partial: dict exists, **never applied** |
| Voice STT/TTS | Missing |
| Farmer map / weather dedicated page / alerts / profile routes | Missing as routes |
| Vercel / Render deployment configs | Missing |
| Frontend/Admin test suites | Missing |
| `VITE_API_BASE_URL` production contract | Missing |
| Expert validation write-back to analysis ground truth | Incomplete |
| Knowledge PDF → Chroma indexing | Fake success path |

---

## 4. Broken / Misleading Features

1. **README claims ViT + YOLO + Mongo telemetry** — code uses color/texture heuristics + memory store.
2. **Admin analytics inflate counts** (`+1420` farmers, `+1040` analyses, hardcoded disease/pest/region charts).
3. **Auth optional** — unauthenticated requests become demo farmer.
4. **Admin portal toggle** — no frontend or backend role gate.
5. **Validation request** hardcodes Tomato / Early Blight regardless of linked analysis.
6. **Knowledge upload** claims Chroma indexing without calling Chroma.
7. **Docker paths** copy `frontend/` and `backend/` but repo uses `Frontend SIH/` and `Backend/`.
8. **i18n** language selector does not translate UI strings.
9. **DosageCalculator** fabricates `2.5 g/L` when dose missing.
10. **Healthy analyses** may still attach pesticide advisory via POP match fallback.
11. **Model registry thresholds** do not wire into inference.
12. **Duplicate data dirs** (`Backend/data` vs `Backend/backend/data`) depending on CWD.

---

## 5. Duplicate Functionality

- Admin UI lives only inside Frontend SIH; `Admin/` is empty (not duplicated — needs extraction).
- API router mounted twice (prefix + root) — convenience, not dual logic.
- Seeded hotspot / validation / analysis demo data overlaps fabricated analytics charts.
- ICAR knowledge exists both as Python dict (`icar_knowledge.py`) and markdown (`knowledge-base/`).

---

## 6. Security Issues

| Issue | Severity |
|-------|----------|
| Soft auth (no token → full demo farmer) | CRITICAL |
| Admin / knowledge / validation / GIS endpoints without role checks | CRITICAL |
| CORS includes `"*"` with `allow_credentials=True` | CRITICAL |
| Hardcoded default `JWT_SECRET` in config, `.env.example`, docker-compose | HIGH |
| Root `.env` present with live secrets (must not be committed) | HIGH |
| Password verify plaintext fallback on bcrypt error | HIGH |
| Register allows client-chosen elevated roles | HIGH |
| Analysis by ID / weak history isolation | HIGH |
| Upload validation is extension/size only (no MIME sniff) | MEDIUM |
| Demo credentials documented in README | LOW (acceptable for SIH demo if labeled) |

---

## 7. Frontend Issues

- God-component `App.tsx` (no router)
- Farmer + Admin in one deployable
- Fabricated KPIs, outbreak ticker, recovery banners, weather fallbacks presented as live
- `TRANSLATIONS` unused
- `getAdminCases` unused; analytics table uses farmer history
- GIS filter stale-state race; `weatherRisk` layer inert
- No loading/empty/error standardization across all screens
- Title still `"frontend"`; leftover Vite CSS
- No production API base URL env
- No vercel.json / SPA rewrites
- Dockerfile folder name mismatch

---

## 8. Backend Issues

- Mongo never written
- ML modules advertise real model names without loading weights
- Crop classifier lists ~20 crops; disease taxonomy covers 6 → mismatch
- Pest detector invents bboxes
- Advisory fallback can recommend wrong crop chemicals
- `email-validator` missing from requirements (Pydantic `EmailStr`)
- Heavy unused deps (`torch`, `ultralytics`, `langchain`) inflate install
- No global exception handler
- Path/CWD sensitivity for uploads and Chroma

---

## 9. Admin Separation Issues

- `Admin/` directory exists but contains **zero** application files
- Admin components under `Frontend SIH/src/components/admin/`
- Portal switch is client-side only
- Backend admin routes are public
- No independent package.json / Vite entry for Admin

---

## 10. AI/ML Issues

| Module | Claimed | Actual |
|--------|---------|--------|
| Gatekeeper | Zero-shot crop filter | ExG vegetation heuristic |
| Crop ID | CropNet-ViT | RGB hash → index |
| Disease | AgriViT / PlantVillage | Necrosis pixel ratio → taxonomy pick |
| Pest | YOLOv8 | Texture std → fake boxes |
| DenseNet121 (Sugarcane/Grapes/Sunflower/Cotton) | Spec assumption | **Not found in repo** |
| Risk fusion | — | Real deterministic rules |

**Decision:** Preserve heuristic pipeline behind clear `inference_mode: heuristic|mock|trained` metadata. Add model abstraction + weight-loading extension points. Do **not** invent DenseNet results.

---

## 11. RAG Issues

- Embeddings are token-hash, not MiniLM
- Knowledge upload does not index
- Assistant retrieval uses weak crop+"General Health" query
- Unmatched disease falls back toward Tomato Early Blight (wrong guidance risk)
- Curated ICAR dict is educational/static — must be labeled as curated knowledge, not live ICAR API
- Groq optional; without key, template/dict path runs

---

## 12. Database Issues

- Intended: MongoDB (`users`, `analyses`, `hotspots`)
- Actual: `memory_store` only — data lost on restart
- Farms collection never populated
- No production persistence strategy documented honestly

---

## 13. Deployment Issues

- docker-compose volume/path names use lowercase `backend/`
- Dockerfiles copy wrong folder names
- No Render `render.yaml` / PORT-aware start
- No Vercel config for Frontend or Admin
- CORS not production-ready
- Compose defaults weak JWT secret

---

## 14. Testing Gaps

| Area | Status |
|------|--------|
| Backend `tests/test_api.py` | Exists; CWD/`email-validator` fragile |
| Authz / role tests | Missing |
| RAG grounding / no-fabricate tests | Missing |
| Persistence tests | Missing |
| Frontend unit/e2e | Missing |
| Admin unit/e2e | Missing |
| Integration upload→history | Partial (diagnose only) |

---

## 15. Priority Classification

### CRITICAL
1. Enforce authentication (reject anonymous privileged actions)
2. Enforce admin role on admin/validation/knowledge write APIs
3. Stop fabricating production analytics numbers
4. Label heuristic/mock AI and pest results honestly in API responses
5. Fix CORS (`*` + credentials)
6. Separate Admin app; gate FARMER out of Admin UI + API
7. Prevent fabricated pesticide advice when knowledge match is weak
8. Fix Docker path mismatches; add production env contracts

### HIGH
9. Persist users/analyses (Mongo when available, else explicit file/JSON store with honesty)
10. Validation request must use real analysis fields
11. Wire model registry thresholds or document as metadata-only
12. Remove dosage `2.5 g/L` silent fabrication
13. Production API base URL for Frontend/Admin
14. Honest README + `.env.example`
15. Knowledge upload/reindex must touch Chroma or report failure

### MEDIUM
16. React Router farmer routes
17. Apply i18n translations
18. Risk engine module clarity (image result vs field risk)
19. PestDetectionService abstraction for future YOLO
20. Weather unavailable vs cached labeling
21. GIS from real cases only (no fake ticker)
22. Global API error handler + frontend error states
23. Slim requirements; add `email-validator`
24. Render + Vercel configs

### LOW
25. Voice STT/TTS extension points
26. Farmer alerts/profile pages when data exists
27. Broader test coverage
28. UI polish / brand consistency

---

## Target Architecture Plan (post-audit)

Prefer keeping existing module boundaries; extract Admin; harden backend; do not replace working heuristics with fake DenseNet.

```
crop_Project_SIH/
├── Admin/                 # Independent Vite React admin app
├── Frontend SIH/          # Farmer-only Vite React app
├── Backend/app/           # Shared FastAPI API
├── infrastructure/        # Docker, render, vercel
├── knowledge-base/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

### Implementation order (this engagement)
1. ✅ Audit (`docs/PROJECT_AUDIT.md`)
2. Critical backend security + honest analytics + AI labeling
3. Persistence improvement (Mongo CRUD with memory fallback)
4. Farmer frontend cleanup (remove admin, router, env, honesty)
5. New Admin app consuming same API with role gate
6. Pest/weather/GIS/validation/risk hardening
7. Tests + Docker + Render + Vercel
8. README + `docs/FINAL_IMPLEMENTATION_REPORT.md`

---

## Explicit Non-Claims

This audit confirms the repository does **not** currently contain:
- Trained DenseNet121 weights for Sugarcane / Grapes / Sunflower / Cotton
- Real Ultralytics YOLO pest weights
- Live ICAR PDF ingestion pipeline
- Production Mongo-backed history across restarts (without further implementation)

Any future SIH pitch materials must align with these facts unless real models are added.
