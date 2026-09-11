# Hugging Face Model Audit — CropShield AI (SIH 2026)

**Date:** 2026-09-11  
**Scope:** Read-only inspection of `crop_Project_SIH` Backend disease path + verification of current HF wiring.  
**Status:** AUDIT COMPLETE — **STOP before multi-model architecture** (see §12 and companion comparison report).

---

## 1. Current disease-detection flow

```
POST /api/v1/diagnose  (alias: /api/v1/analysis/run)
  → storage_service.save_image (magic bytes + PIL)
  → gatekeeper.inspect (ExG heuristic; reject if non-crop)
  → crop_classifier.identify (crop_hint preferred; else color-hash)
  → disease_model.inference(image_bytes, detected_crop)   [thread]
  → pest_detector.detect (unavailable by default)
  → weather_service (Open-Meteo or unavailable)
  → risk_engine.calculate_risk
  → advisory_engine.generate_advisory (RAG / ICAR match / optional Groq)
  → persist_analysis (Mongo or memory)
  → AnalysisResponse
```

**Files:**
- `Backend/app/api/v1/analysis.py`
- `Backend/app/ml/gatekeeper.py`
- `Backend/app/ml/crop_classifier.py`
- `Backend/app/ml/disease_classifier.py`
- `Backend/app/ml/hf_plantvillage.py`
- `Backend/app/ml/pest_detector.py`
- `Backend/app/ml/risk_fusion.py`
- `Backend/app/rag/advisory_engine.py`

---

## 2. Current Hugging Face model(s)

| Setting | Value |
|---------|--------|
| Env `HF_DISEASE_MODEL_ID` | default `kimcomehome/plantvillage-vit-leaf-disease` |
| Env `USE_HF_DISEASE_MODEL` | default `true` |
| Env `HF_TOKEN` | optional (public model does not require token) |
| Env `USE_MOCK_AI` | if `true`, skips HF (tests only) |

**Verified from Hub `config.json` (2026-09-11):**  
Architecture `ViTForImageClassification`, 38 `id2label` PlantVillage classes, `image_size: 224`.

---

## 3. Model loading method

- Lazy load via `transformers.pipeline("image-classification", model=...)`
- Cached on `HuggingFacePlantVillageClassifier._pipe` (singleton)
- Device: CUDA if available else CPU (`device=0` / `-1`)
- Weights: Hugging Face Hub → local HF cache (not baked into Docker by default)
- **Does not** load `.keras` DenseNet files from outside this directory

---

## 4. Input image preprocessing

- PIL `RGB` open from upload bytes
- Pipeline applies ViT image processor (resize/normalize to 224×224 per model config)
- No custom OpenCV pipeline beyond gatekeeper/crop heuristics

---

## 5. Output labels/classes (VERIFIED from config.json)

Exact `id2label` (38):

Apple (4), Blueberry healthy, Cherry (2), Corn/maize (4), Grape (4), Orange HLB, Peach (2), Pepper bell (2), Potato (3), Raspberry healthy, Soybean healthy, Squash powdery mildew, Strawberry (2), Tomato (10).

Full list is in Hub config; parser in `hf_plantvillage.parse_plantvillage_label` splits `Crop___Disease`.

---

## 6. Confidence calculation

- Pipeline returns softmax scores per class
- Top-1 (or top among crop-filtered scores) `score` used as `confidence`
- Confidence threshold `0.65` on `DiseaseModel` used for low-confidence **note** only (does not invent alternate disease)

---

## 7. Supported crops (by current HF model — VERIFIED)

Tomato, Potato, Grape, Maize/Corn, Apple, Cherry, Peach, Pepper, Strawberry, Orange, Blueberry, Raspberry, Soybean (healthy-only), Squash (powdery mildew).

---

## 8. Unsupported crops (relative to SIH targets)

| Crop | Status vs current HF model |
|------|----------------------------|
| Sugarcane | **Not in PlantVillage labels** |
| Cotton | **Not in PlantVillage labels** |
| Sunflower | **Not in PlantVillage labels** |
| Rice | **Not in PlantVillage labels** |
| Wheat | **Not in PlantVillage labels** |

---

## 9. Heuristic / demo code

| Component | Mode | Notes |
|-----------|------|-------|
| Gatekeeper | Heuristic ExG | Not disease diagnosis |
| Crop ID | Heuristic color-hash unless `crop_hint` | Prefer farmer hint |
| Disease (legacy) | Necrosis taxonomy | **Removed from production path** (Phase 6); only `USE_MOCK_AI` test stub remains |
| Pest | Unavailable / optional mock | Unchanged |
| Seed demo analyses | Demo labels | Only if `SEED_DEMO_DATA` and not production |

**Prior gap (fixed in this pass):** HF fail / uncovered crop previously fell back to heuristic disease names. Production now returns `inference_mode=unavailable` and API `status=model_unavailable`.

---

## 10. Dependencies

`Backend/requirements.txt`: FastAPI stack + `torch`, `transformers`, Pillow, numpy, chromadb, groq, motor, etc.  
No `pyproject.toml`.  
Docker: `infrastructure/Dockerfile.backend` installs requirements; does **not** pre-download HF weights.  
Render: `infrastructure/render/render.yaml` — no `USE_HF_DISEASE_MODEL` / `HF_DISEASE_MODEL_ID` env yet.

---

## 11. Problems / gaps

1. **Single PlantVillage model cannot cover SIH priority crops** (Sugarcane, Cotton, Sunflower).
2. **Silent heuristic fallback existed** → corrected to unavailable (this change set).
3. **No real inference smoke test** in CI (tests set `USE_MOCK_AI=true`).
4. **Render free tier risk:** torch + ~86M ViT download + cold start RAM/time.
5. **Crop auto-ID still heuristic** — disease routing depends on accurate `crop_hint`.
6. **Multi-model registry not implemented** — stopped pending verified crop→model map (see comparison doc).
7. **Cotton / Sunflower:** research found **no verified** HF transformers classifier with those classes in config at audit time.

---

## 12. Recommended architecture (DESIGN ONLY — not fully implemented)

```
crop_hint (required for routing)
    ↓
model_registry[crop] → { hf_model_id, labels, preprocess, framework }
    ↓
hf_model_loader (cached)
    ↓
disease + confidence (real softmax)
    ↓
if confidence < τ → flag uncertainty + expert validation CTA
    ↓
RAG advisory on ACTUAL disease only
    ↓
persist history + inference_meta.model_id
```

**Populate registry only after label verification.** Crops without a verified model stay `model_unavailable`.

**STOP:** Do not replace architecture with multi-model loading until Crop→Model table is approved (comparison doc § Recommendations).

---

## Related docs

- `docs/HUGGINGFACE_MODEL_COMPARISON.md`
- `docs/HUGGINGFACE_INTEGRATION_REPORT.md`
