# Final Backend Verification

**Date:** 2026-09-11  
**Scope:** Live HF → RAG (real diagnose API) + MongoDB durable persistence + Docker re-check  
**Constraints honored:** no pest AI, no frontend redesign, no HF architecture changes, no disease hardcoding

Evidence:

- `docs/_live_hf_rag_result.json`
- `docs/_mongo_persistence_result.json`
- `docs/_pytest_full.log`
- Prior E2E: `docs/END_TO_END_VERIFICATION_REPORT.md`

---

## 1. HF Disease Detection

**Status: PASS**

- `USE_MOCK_AI=false`
- Health: `disease_inference=HUGGINGFACE_MULTI_MODEL`
- Live `POST /api/v1/diagnose` returned `inference_mode=huggingface_trained`
- Real HF smoke suite: **8/8 passed** (`tests/test_hf_real_smoke.py`)

---

## 2. Crop Routing

**Status: PASS**

Verified map (prior E2E + health `hf_models`):

| Crop | Model |
|------|-------|
| Grape / Tomato / PlantVillage crops | `kimcomehome/plantvillage-vit-leaf-disease` |
| Sugarcane | `LishaV01/agriculture-crop-disease-detection` |
| Rice / Wheat | `wambugu71/crop_leaf_diseases_vit` |
| Cotton | `YaswanthReddy23/ViT_Cotton` |
| Sunflower | `YaswanthReddy23/ViT_Sunflower` |

Live RAG test used `crop_hint=Tomato` → PlantVillage model (confirmed).

---

## 3. Live HF → RAG

**Status: PASS — LIVE HF → RAG MISS**

Full production path exercised (no hardcoded disease, no post-inference label substitution):

```
image (multipart)
→ JWT auth
→ gatekeeper
→ crop_hint=Tomato
→ HF PlantVillage ViT
→ predicted disease (model softmax only)
→ AdvisoryEngine._match_record(crop, disease)
→ unavailable advisory (no KB pair)
→ HTTP 200 AnalysisResponse
```

### Captured fields

| Field | Value |
|-------|-------|
| crop | Tomato |
| raw_label | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` |
| display_label | Tomato Yellow Leaf Curl Virus |
| confidence | 0.065057 |
| model_id | `kimcomehome/plantvillage-vit-leaf-disease` |
| RAG query/key | crop=`Tomato`, disease=`Tomato Yellow Leaf Curl Virus` |
| RAG hit/miss | **MISS** |
| recommendation status | `guidance_available=false`, empty dose, consult KVK |
| response status | `completed` (HTTP 200) |
| analysis_id | `an_1e37185bd4` |

### Normalization (existing architecture only)

`AdvisoryEngine._match_record`:

- case-insensitive **crop equality**
- disease match if KB disease is a substring of the predicted name (or vice versa)
- healthy special-case only when `"healthy"` appears in the disease name
- **no** rewrite of HF `raw_label` / `display_label` in the diagnose path

Tomato KB currently has **Early Blight** only; YLCV does not match → miss is correct.

*(Prior advisory-engine unit check with Early Blight still demonstrates a true KB hit path; this live HTTP run did not alter predictions to force that.)*

---

## 4. RAG Safety

**Status: PASS**

On this live miss:

- `exact_dose_per_liter` = `""`
- chemical = `Verified chemical guidance unavailable`
- `invented_dosage_on_miss` = **false**
- summary explicitly states verified guidance unavailable / expert review

---

## 5. Memory Storage

**Status: PASS**

- Running API reported `persistence_mode=memory`, `mongodb_connected=false`
- Live diagnosis `an_1e37185bd4` retrievable via farmer `GET /api/v1/analysis/history` in the same process
- Prior E2E: cross-farmer isolation 403

Memory is **non-durable across process restart**.

---

## 6. MongoDB Durable Storage

**Status: BLOCKED**

Configured URI points at local Mongo (`host_hint=localhost`), DB name set.

Verification script `scripts/verify_mongo_persistence.py`:

- connection attempt → failed (no server on port 27017)
- `mongod` / `mongosh` not installed on PATH
- Docker Engine unavailable → cannot start a Mongo container as workaround

**No durable write/read/restart test was possible.** Do not claim Mongo persistence.

---

## 7. Restart Persistence

**Status: BLOCKED** (depends on MongoDB)

Cannot verify survival of diagnosis records across backend restart without a live Mongo connection.

Expected when Mongo is available: `persist_analysis` upserts into `analyses` and `hydrate_memory_from_mongo` reloads on startup.

---

## 8. Admin Persistence

**Status: BLOCKED** (depends on MongoDB restart)

Admin API itself previously **PASS** in-process (stats/cases/models).  
Admin visibility of a diagnosis **after process restart** was not verified.

---

## 9. Security

**Status: PASS** (from prior E2E + suite)

- Auth required on diagnose; invalid token 401
- Farmer cannot access admin endpoints (403)
- Upload validation: bad type / oversized / corrupt / empty → 400
- Production guards reject `USE_MOCK_AI`, demo seed/auth, weak JWT, empty CORS

Full suite: **26 passed**

---

## 10. Docker

**Status: BLOCKED**

```
DOCKER VERIFICATION BLOCKED — DOCKER ENGINE UNAVAILABLE
```

Docker CLI present; daemon pipe `dockerDesktopLinuxEngine` not running.  
No image build, no container health, no in-container HF inference.

---

## 11. Remaining Limitations

1. **MongoDB not running locally** — durable persistence, restart survival, and admin-after-restart unverified.
2. **Docker Engine unavailable** — container/deploy path unverified.
3. **Live HF → RAG HIT** not observed on this HTTP run (model predicted YLCV; KB has Tomato Early Blight). Miss path correctness verified; hit path previously verified only via advisory engine with Early Blight (not by altering this live prediction).
4. Synthetic leaf images → low confidence labels; not field accuracy claims.
5. Pest AI still unavailable (by design for this phase).
6. **Not production-ready** until Mongo + Docker (or equivalent hosting) are evidenced.

---

## Test commands executed

| Suite | Command | Result |
|-------|---------|--------|
| Full unit/API + HF smoke + unsupported | `python -m pytest tests -v` | **26 passed** |
| Real HF smoke (included above) | `tests/test_hf_real_smoke.py` | **8 passed** |
| Live HF → RAG | `python scripts/verify_live_hf_rag.py` | **PASS — LIVE HF → RAG MISS** |
| Mongo persistence | `python scripts/verify_mongo_persistence.py` | **BLOCKED** (exit 2) |
| Docker | `docker version` / engine check | **BLOCKED** |

---

## Scorecard

| Area | Status |
|------|--------|
| HF disease detection | PASS |
| Crop routing | PASS |
| Live HF → RAG | PASS (**MISS**) |
| RAG safety | PASS |
| Memory storage | PASS |
| MongoDB durable storage | **BLOCKED** |
| Restart persistence | **BLOCKED** |
| Admin after restart | **BLOCKED** |
| Security | PASS |
| Docker | **BLOCKED** |

**Verdict:** Live HF → RAG integration is correct (miss with safe unavailable advisory). Durable Mongo and Docker remain **BLOCKED**. Production readiness is **not** claimed.
