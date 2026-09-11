# End-to-End Diagnosis Flow Verification Report

**Date:** 2026-09-11  
**Environment under test:** local development (`ENVIRONMENT=development`, `USE_MOCK_AI=false`, `USE_HF_DISEASE_MODEL=true`)  
**API base:** `http://127.0.0.1:8001/api/v1`  
**Auth:** farmer `demo@cropshield.ai`, admin `admin@cropshield.ai`  
**Evidence artifact:** `docs/_e2e_results.json`  
**Harness:** `Backend/scripts/e2e_diagnosis_verification.py` (real HTTP multipart requests)

---

## Status legend

| Status | Meaning |
|--------|---------|
| **PASS** | Verified with evidence |
| **FAIL** | Verified broken |
| **BLOCKED** | Could not run the required check |
| **NOT TESTED** | Not executed in this pass |

---

## 1. Architecture flow

```
Frontend FormData (file + lat/lon + optional crop_hint + Bearer token)
  → POST /api/v1/diagnose
  → get_current_user (JWT)
  → StorageService.save_image (ext / MIME / magic / PIL / size)
  → Gatekeeper (ExG plant presence)
  → CropClassifier (prefer crop_hint → user_hint mode)
  → DiseaseModel → HF crop registry → HF model loader → preprocess → softmax
  → PestDetector (unavailable unless mock/trained path)
  → Weather (optional coords)
  → Risk fusion
  → AdvisoryEngine / RAG (skipped disease-conditioned dosage when model_unavailable)
  → persist_analysis (memory or Mongo)
  → AnalysisResponse (+ history record with model metadata)
```

**Status:** PASS (code path inspected; live HTTP exercised)

### Observed request/response contract

| Layer | Field / behavior | Match? |
|-------|------------------|--------|
| Frontend `api.runDiagnosis` | `POST ${API_BASE}/diagnose`, FormData, Bearer | Yes |
| Frontend upload | `file`, `latitude`, `longitude`, optional `crop_hint` | Yes |
| Backend | `UploadFile file`, Form `crop_hint`, auth required | Yes |
| Registry | Crop → verified HF `model_id` | Yes |
| Response | `status`, `crop`, `disease`, `confidence`, `inference_meta`, advisory | Yes |
| History | Includes `model.provider/model_id/architecture`, labels, `user_id` | Yes |
| `model_unavailable` | `disease=null`, `confidence=null`, no fake disease | Yes |

---

## 2. API endpoint tested

| Endpoint | Result |
|----------|--------|
| `GET /api/v1/health` | PASS — `disease_inference=HUGGINGFACE_MULTI_MODEL` |
| `POST /api/v1/auth/login` | PASS |
| `POST /api/v1/diagnose` | PASS (crops + security cases) |
| `GET /api/v1/analysis/history` | PASS |
| `GET /api/v1/analysis/{id}` | PASS (incl. 403 cross-farmer) |
| `GET /api/v1/admin/stats` | PASS (after fix) |
| `GET /api/v1/admin/cases` | PASS |
| `GET /api/v1/admin/models` | PASS |

---

## 3. Authentication tested

| Case | HTTP | Status |
|------|------|--------|
| Farmer login | 200 | PASS |
| Admin login | 200 | PASS |
| Diagnose without token | 401 | PASS |
| Diagnose with invalid token | 401 | PASS |
| Farmer → `/admin/stats` | 403 | PASS |
| Admin → `/admin/stats` | 200 | PASS |

---

## 4. Crop routing

| Crop | Expected model | Observed `hf_disease_model_id` / `model_id` | Match |
|------|----------------|-----------------------------------------------|-------|
| Grape | `kimcomehome/plantvillage-vit-leaf-disease` | same | PASS |
| Sugarcane | `LishaV01/agriculture-crop-disease-detection` | same | PASS |
| Rice | `wambugu71/crop_leaf_diseases_vit` | same | PASS |
| Wheat | `wambugu71/crop_leaf_diseases_vit` | same | PASS |
| Cotton | `YaswanthReddy23/ViT_Cotton` | same | PASS |
| Sunflower | `YaswanthReddy23/ViT_Sunflower` | same | PASS |

No cross-model selection observed.

---

## 5. Real inference (HTTP, not class-only)

Synthetic vegetative JPEG uploads (gatekeeper-passable). Labels are model softmax outputs on non-field photos — **not accuracy claims**.

| Crop | HTTP | API status | Disease | Confidence | Provider | Model ID |
|------|------|------------|---------|------------|----------|----------|
| Grape | 200 | completed | Esca (Black Measles) | 0.017 | huggingface | kimcomehome/plantvillage-vit-leaf-disease |
| Sugarcane | 200 | completed | Healthy Crop | 0.044 | huggingface | LishaV01/agriculture-crop-disease-detection |
| Rice | 200 | completed | Brown Spot | 0.440 | huggingface | wambugu71/crop_leaf_diseases_vit |
| Wheat | 200 | completed | Healthy Crop | 0.047 | huggingface | wambugu71/crop_leaf_diseases_vit |
| Cotton | 200 | completed | Bacterial Blight | 0.275 | huggingface | YaswanthReddy23/ViT_Cotton |
| Sunflower | 200 | completed | Leaf scars | 0.292 | huggingface | YaswanthReddy23/ViT_Sunflower |

**Status:** PASS for pipeline + routing + real HF inference.  
**Not claimed:** field-level diagnostic accuracy.

---

## 6. Unsupported crop

| Crop | HTTP | status | disease | confidence |
|------|------|--------|---------|------------|
| Millet | 200 | `model_unavailable` | `null` | `null` |

No fabricated disease name. **PASS**

---

## 7. RAG

### A) Disease **without** knowledge-base match (live HF → API)

Examples from HTTP runs (Grape/Esca, Rice/Brown Spot, Tomato/YLCV, Cotton/Bacterial Blight, Sunflower/Leaf scars):

- `guidance_available=false`
- `exact_dose_per_liter=""`
- chemical labeled unavailable / consult KVK
- advisory text states verified guidance unavailable

**Status:** PASS — no invented dosage on miss

### B) Disease **with** knowledge-base entry

Live HF labels from synthetic leaves did **not** land on a curated pair (e.g. Tomato Early Blight).

Advisory-engine check with HF-shaped `DiseasePrediction(disease="Early Blight")` for Tomato:

- `guidance_available=True`
- dose `2.5 g/L` (Mancozeb / Dithane M-45) from curated ICAR-style record
- 1 source reference returned

**Status:** PASS for RAG retrieval when disease matches KB  
**Status:** NOT TESTED for full HTTP HF-label → KB-hit on a real field photo (no matching synthetic prediction)

---

## 8. History

After Grape diagnosis, farmer history contained:

| Field | Present |
|-------|---------|
| crop | Grape |
| disease | Esca (Black Measles) |
| confidence | yes |
| raw_label | `Grape___Esca_(Black_Measles)` |
| display_label | Esca (Black Measles) |
| model.provider | huggingface |
| model.model_id | kimcomehome/plantvillage-vit-leaf-disease |
| model.architecture | ViTForImageClassification |
| timestamp (`created_at`) | yes |
| user_id | `usr_demo_farmer` |

Cross-farmer isolation:

- Second registered farmer `GET /analysis/{grape_id}` → **403**
- Second farmer history does not include grape id

**Status:** PASS  
**Note:** persistence mode was **memory** (MongoDB unavailable locally) — durable Mongo history NOT TESTED.

---

## 9. Admin access

| Check | Result | Status |
|-------|--------|--------|
| Farmer blocked from admin stats | 403 | PASS |
| Admin stats after null-disease fix | 200 | PASS |
| Admin cases list | 200, count includes diagnoses | PASS |
| Admin models registry | 200 | PASS |
| Model ID/provider traceable on diagnosis records | yes (`model` on history/case) | PASS |
| Secrets in admin payloads | none observed (no JWT/GROQ) | PASS |

Admin UI uses the same `/api/v1/admin/*` contracts (`Admin/src/services/api.ts`). Browser UI click-through: **NOT TESTED** (API verified).

---

## 10. Frontend ↔ backend contract

| Item | Status | Notes |
|------|--------|-------|
| API base URL | PASS | `VITE_API_BASE_URL` or `/api/v1` |
| Bearer token | PASS | `cropshield_token` |
| Multipart upload | PASS | FormData `file` |
| `crop_hint` | PASS | appended when provided |
| Response parsing | PASS | navigates on non-rejected |
| `model_unavailable` | PASS (after fix) | types + null-safe disease display |
| Recommendation display | PASS | DosageCalculator respects `guidance_available===false` |
| History display | PASS (after fix) | null disease safe |

**Integration bugs fixed (minimal UI, no redesign):**

1. `DiseasePrediction.disease/confidence` typed nullable; `status` includes `model_unavailable`
2. `ReportView` / dashboard / history / pages null-safe pathology labels

---

## 11. Invalid-input security

| Case | HTTP | Status |
|------|------|--------|
| `.txt` upload | 400 | PASS |
| Oversized (>10MB) | 400 | PASS |
| Corrupted JPEG | 400 | PASS |
| Empty upload | 400 | PASS |
| Missing auth | 401 | PASS |
| Invalid auth | 401 | PASS |
| Farmer vs admin | 403 / 200 | PASS |
| Missing `crop_hint` | N/A | Hint is **optional**; classifier uses heuristic fallback among supported crops — not a hard 400 |

Upload security rules were **not** weakened.

---

## 12. Production configuration

Validated via `validate_runtime_settings` (development + production guard matrix):

| Rule | Result |
|------|--------|
| `USE_MOCK_AI=true` in production | BLOCKED at startup |
| `SEED_DEMO_DATA=true` in production | BLOCKED |
| `ALLOW_DEMO_AUTH=true` in production | BLOCKED |
| Weak / known placeholder `JWT_SECRET` | BLOCKED |
| Empty production CORS | BLOCKED |
| `*` stripped from CORS parser | PASS |
| Valid production config | ALLOWED |

Local `.env` contains a known-placeholder JWT and API keys for development; `.gitignore` lists `.env`. This workspace is **not** a git repository, so “no secrets committed” cannot be fully proven here → **BLOCKED** (no git history to audit).

---

## 13. Docker status

```
DOCKER VERIFICATION BLOCKED — DOCKER ENGINE UNAVAILABLE
```

Docker CLI is installed (`29.6.2`), but the engine pipe `dockerDesktopLinuxEngine` is not running.  
**No image build, no container health check, no in-container HF inference was performed.**  
Do **not** treat Docker/Render readiness as PASS.

`infrastructure/Dockerfile.backend` was inspected (production env defaults, fails closed on secrets) — inspection only.

---

## 14. Performance

Measured **total API wall time** (includes first-load model download/cache on cold start). Separate pure-inference-only timers were not instrumented in the HTTP harness; cold Grape includes PlantVillage load.

| Crop | Model | Total API time (ms) |
|------|-------|---------------------|
| Grape | kimcomehome/plantvillage-vit-leaf-disease | 28514.8 (cold) |
| Sugarcane | LishaV01/agriculture-crop-disease-detection | 2257.3 |
| Rice | wambugu71/crop_leaf_diseases_vit | 2192.8 |
| Wheat | wambugu71/crop_leaf_diseases_vit | 55.7 (warm) |
| Cotton | YaswanthReddy23/ViT_Cotton | 2967.6 |
| Sunflower | YaswanthReddy23/ViT_Sunflower | 3382.1 |
| Millet (unavailable) | — | 20.8 |

No performance optimization applied (none required for correctness).

---

## 15. Bugs found

1. **FAIL → fixed:** `GET /api/v1/admin/stats` crashed (`AttributeError`) when any analysis had `disease.disease is None` (`model_unavailable`). Same pattern risk on `/admin/diseases`.
2. **FAIL → fixed:** Farmer frontend could crash / show bad pathology UI when `disease`/`confidence` were null (`model_unavailable`).
3. **Observation:** Admin cases sample may include seed/`model_unavailable` rows with `model_id=null` — expected; successful HF rows carry full model metadata.
4. **Observation:** Low softmax confidence on synthetic leaves — expected; not treated as a routing bug.

---

## 16. Fixes applied

| File | Change |
|------|--------|
| `Backend/app/api/v1/admin.py` | Null-safe disease aggregation for analytics + disease summary |
| `Frontend SIH/src/types/index.ts` | Nullable disease/confidence; `model_unavailable` status |
| `Frontend SIH/src/components/farmer/ReportView.tsx` | Null-safe pathology display |
| `Frontend SIH/src/components/farmer/FarmerDashboard.tsx` | Null-safe disease label |
| `Frontend SIH/src/components/farmer/FarmerHistory.tsx` | Null-safe disease label |
| `Frontend SIH/src/pages/FarmerPages.tsx` | Null-safe disease label |
| `Backend/scripts/e2e_diagnosis_verification.py` | HTTP E2E harness (new) |

**Not changed:** HF model registry, model architecture, pest AI, UI redesign.

---

## 17. Remaining issues

1. **DOCKER VERIFICATION BLOCKED** — start Docker Desktop and re-run build + container HF diagnose before claiming deploy readiness.
2. **MongoDB persistence NOT TESTED** — local run used in-memory store.
3. **Live HF → RAG KB-hit on real leaf photo NOT TESTED** — miss path verified over HTTP; hit path verified via advisory engine with Early Blight.
4. **Admin browser UI click-through NOT TESTED** — API contracts verified.
5. **Git secret audit BLOCKED** — no `.git` in this workspace.
6. Cold-start first model load is multi-second on CPU — operational note, not a correctness failure.
7. Production readiness is **not claimed** until Docker + Mongo + real deploy config are evidenced.

---

## Section scorecard

| # | Area | Status |
|---|------|--------|
| 1 | Architecture flow | PASS |
| 2 | API endpoints | PASS |
| 3 | Authentication | PASS |
| 4 | Crop routing | PASS |
| 5 | Real inference (6 crops) | PASS |
| 6 | Unsupported crop | PASS |
| 7 | RAG (miss HTTP / hit engine) | PASS / partial NOT TESTED for live HF→KB-hit |
| 8 | History + isolation | PASS |
| 9 | Admin access | PASS |
| 10 | Frontend/backend contract | PASS (bugs fixed) |
| 11 | Invalid-input security | PASS |
| 12 | Production config guards | PASS |
| 13 | Docker | **BLOCKED** |
| 14 | Performance measured | PASS (measure only) |

**Overall:** End-to-end diagnosis path over real HTTP with Hugging Face multi-model routing is verified for the six target crops, unsupported crop, RAG miss behavior, history isolation, admin API, and upload/auth security. **Docker remains BLOCKED. Production readiness is not claimed.**
