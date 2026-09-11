# Hugging Face Integration Report — CropShield AI (SIH 2026)

**Date:** 2026-09-11  
**Legend:** IMPLEMENTED | VERIFIED | UNVERIFIED | FUTURE

---

## 1. Final selected model(s)

| Role | Model ID | Status |
|------|----------|--------|
| Primary (PlantVillage crops) | `kimcomehome/plantvillage-vit-leaf-disease` | **IMPLEMENTED** wiring + **VERIFIED** labels |
| Rice / Wheat / Sugarcane multi-crop | `LishaV01/agriculture-crop-disease-detection` or `wambugu71/crop_leaf_diseases_vit` | **FUTURE** (researched; not integrated) |
| Heavy multi-crop alt | `Arko007/nfnet-f1-plant-disease` | **FUTURE** (labels VERIFIED; stack/deploy UNVERIFIED) |
| Cotton | — | **NO VERIFIED MODEL** |
| Sunflower | — | **NO VERIFIED MODEL** |

---

## 2. Exact Hugging Face model IDs

- **Active:** `kimcomehome/plantvillage-vit-leaf-disease`
- **Researched (not active):** see `docs/HUGGINGFACE_MODEL_COMPARISON.md`

---

## 3. Why selected

- Verified 38-class `id2label` in Hub config  
- Native `transformers` image-classification pipeline (matches FastAPI backend)  
- Card documents coverage limits honestly (does not claim millet/sorghum/etc.)  
- Public model; token optional  

**Why not sole SIH solution:** no Sugarcane / Cotton / Sunflower / Rice / Wheat classes.

---

## 4. Dataset

PlantVillage (Mohanty et al. / standard leaf disease benchmark). Lab-style images — domain shift to field photos is a known limitation (card notes).

---

## 5. Supported crops (active model)

VERIFIED: Tomato, Potato, Grape, Maize/Corn, Apple, Cherry, Peach, Pepper, Strawberry, Orange, Blueberry, Raspberry, Soybean (healthy), Squash (powdery mildew).

---

## 6. Disease classes

38 PlantVillage labels — full list in Hub `config.json` and audit doc §5.

---

## 7. Reported metrics

From model card (not re-run here): overall Acc ≈ 0.9979; maize Acc 0.9844 / macro F1 0.9785.  
**UNVERIFIED** by CropShield benchmark suite.

---

## 8. Actual inference verification

| Check | Result |
|-------|--------|
| Config / label verification via Hub | **PASS (VERIFIED)** |
| Local torch/transformers load + image inference | **UNVERIFIED** this session (no mandatory smoke run after research STOP) |
| API end-to-end with real HF weights | **UNVERIFIED** |
| Automated pytest | Uses `USE_MOCK_AI=true` — **not** real HF inference |

Do **not** treat integration as complete for production AI claims until a real smoke test PASSes.

---

## 9. Preprocessing

PIL RGB → ViT image processor (224×224) inside `transformers` pipeline.

---

## 10. Architecture (current)

```
IMAGE → gatekeeper → crop_hint/heuristic crop
  → HF PlantVillage if crop covered
  → else status=model_unavailable (no fake disease)
  → RAG only on real disease when available
  → history
```

Multi-model registry: **FUTURE** (designed in audit/comparison; not coded).

---

## 11. RAG integration

**PRESERVED.**  
When `disease.inference_mode == unavailable`, advisory uses unavailable path (no chemical invention).  
When HF succeeds, RAG receives the **actual** predicted disease string.

---

## 12. API changes

- `status` may be `model_unavailable` when no HF disease prediction  
- `inference_meta` includes `disease_inference_mode`, `disease_model_name`, `hf_disease_model_id`  
- Persisted `model` object on analysis record: provider / model_id / architecture / status  
- Frontend not redesigned  

---

## 13. Deployment requirements (Render)

| Item | Recommendation |
|------|----------------|
| Packages | `torch` + `transformers` already in requirements (image size ↑) |
| Model download | Lazy on first diagnose; or bake into Docker for cold-start control |
| Auth | Public model — **no HF token required** |
| RAM | Prefer paid Render plan if loading ViT-B; free tier may OOM/timeout |
| Env | Set `USE_HF_DISEASE_MODEL=true`, `HF_DISEASE_MODEL_ID=kimcomehome/plantvillage-vit-leaf-disease` |
| Do not | Bundle unrelated `.keras` from other folders |

---

## 14. Known limitations

- PlantVillage domain shift  
- Unsupported SIH crops return unavailable  
- Crop ID without hint still heuristic  
- Pest still unavailable without YOLO  
- Real HF smoke test pending  

---

## 15. Unsupported crops/classes

Cotton, Sunflower (no verified HF model).  
Sugarcane / Rice / Wheat: researched candidates only — **not** in active registry.

---

## 16. Future model expansion plan

1. Approve crop→model table from comparison doc  
2. Implement `model_registry` + cached `hf_model_loader`  
3. Wire `wambugu71` or `LishaV01` for Rice/Wheat/(Sugarcane) after smoke PASS  
4. Source or train Cotton & Sunflower models; publish to Hub with clear `id2label`  
5. Optional: evaluate `Arko007` on paid instance  
6. Add `tests/test_hf_inference_smoke.py` gated by `RUN_HF_SMOKE=1`  

---

## Changes made in this research pass (IMPLEMENTED)

1. Docs: AUDIT, COMPARISON, this REPORT  
2. Production disease path: **removed silent heuristic disease fallback**  
3. API: `model_unavailable` + no RAG dosage when model missing  

## Explicitly NOT done (STOP)

- Multi-model registry implementation  
- Switching primary model away from PlantVillage without approval  
- Claiming Cotton/Sunflower support  
- Real HF inference smoke (marked UNVERIFIED)  
