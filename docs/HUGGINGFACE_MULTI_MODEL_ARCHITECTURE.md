# Hugging Face Multi-Model Architecture — CropShield AI

**Date:** 2026-09-11 (updated: Cotton + Sunflower integrated)  
**Status:** Verified multi-model registry **IMPLEMENTED** for listed crops

---

## 1. Architecture diagram

```
IMAGE upload
    ↓
Gatekeeper (ExG — presence only)
    ↓
crop_hint (preferred) | heuristic_uncertain crop ID
    ↓
hf_crop_registry.resolve_spec(crop)
    ↓
┌──────────────────────────────────────────────┐
│ Verified route?                              │
│  YES → hf_model_loader (lazy cache)          │
│        → AutoImageProcessor                  │
│        → softmax → raw_label + confidence    │
│  NO  → status=model_unavailable              │
│        disease=null, confidence=null         │
└──────────────────────────────────────────────┘
    ↓
RAG (real disease only; else unavailable guidance)
    ↓
History + Admin-visible model metadata
```

---

## 2. Model registry

| Module | Role |
|--------|------|
| `hf_crop_registry.py` | Crop → verified HF model |
| `hf_model_loader.py` | Lazy thread-safe cache |
| `hf_disease_classifier.py` | Inference + crop filter / specialist |
| `disease_classifier.py` | API `DiseasePrediction` wrapper |

---

## 3–4. Crop routing & model IDs

| Crop | Model | Status |
|------|-------|--------|
| Grape | `kimcomehome/plantvillage-vit-leaf-disease` | VERIFIED |
| Tomato | `kimcomehome/plantvillage-vit-leaf-disease` | VERIFIED |
| Potato | `kimcomehome/plantvillage-vit-leaf-disease` | VERIFIED |
| Maize/Corn | `kimcomehome/plantvillage-vit-leaf-disease` | VERIFIED |
| Apple, Cherry, Peach, Pepper, Strawberry, Orange, Blueberry, Raspberry, Soybean, Squash | PlantVillage (verified labels) | VERIFIED |
| Sugarcane | `LishaV01/agriculture-crop-disease-detection` | VERIFIED |
| Rice | `wambugu71/crop_leaf_diseases_vit` | VERIFIED |
| Wheat | `wambugu71/crop_leaf_diseases_vit` | VERIFIED |
| Cotton | `YaswanthReddy23/ViT_Cotton` | VERIFIED |
| Sunflower | `YaswanthReddy23/ViT_Sunflower` | VERIFIED |

Env: `HF_MODEL_PLANTVILLAGE`, `HF_MODEL_SUGARCANE`, `HF_MODEL_RICE`, `HF_MODEL_WHEAT`, `HF_MODEL_COTTON`, `HF_MODEL_SUNFLOWER`.

---

## 5. Supported / unsupported

**Supported:** table above.  
**Unsupported examples:** Millet, Sorghum, Chickpea, and any crop not in the registry → `model_unavailable`.

---

## 6. Cotton / Sunflower label notes

**Cotton raw labels:** Bacterial Blight, Curl Virus, Healthy Leaf, Herbicide Growth Damage, Leaf Hopper Jassids, Leaf Redding, Leaf Variegation.  
→ No `cotton` token in labels; specialist model (`crop_filter_tokens=[]`); crop from `crop_hint`.

**Sunflower raw labels:** Downy mildew, Gray mold, Healthy, Leaf scars.  
→ Same specialist pattern.

---

## 7. Preprocessing

Per-model `AutoImageProcessor` from Hub. No DenseNet preprocessing.

---

## 8–9. Confidence & RAG

Confidence = softmax probability (not accuracy).  
RAG uses actual predicted disease; on miss → guidance unavailable (no invented dosage).

---

## 10. History

Stores crop, disease, confidence, raw_label, display_label, model provider/id/architecture, timestamps via analysis persist.

---

## 11. Metric caveats

**MODEL-CARD METRIC ≠ OUR SYSTEM ACCURACY.**

**Sunflower:** Hub card Acc 0.9709 vs `eval_results.json` Acc ≈ 0.38 — **evaluation metric conflict**. The model has successful real inference, but **no accuracy figure is claimed for this model in the project.**

Cotton card Acc 0.9859 is a **model-card metric only**, not CropShield benchmarked accuracy.

---

## 12. Deployment (Render)

Five model families (3× ViT-B ≈ 86M each + 2× ViT-Tiny ≈ 5.5M).  
**Lazy load only** — do not preload all five.  
Cold start / RAM risk on free tier; prefer paid plan if multiple crops warm.  
Health exposes `hf_models` / supported crop lists (no secrets).

---

## 13. Future

Pest AI, weather risk models, Digital Twin — **NOT IMPLEMENTED**.

---

## IMPLEMENTED

- PlantVillage, Lisha sugarcane, wambugu rice/wheat  
- Cotton `YaswanthReddy23/ViT_Cotton`  
- Sunflower `YaswanthReddy23/ViT_Sunflower`  
- Unsupported → model_unavailable  
- No production heuristic disease fallback  

## NOT IMPLEMENTED

- Pest AI / YOLO  
- Environmental / geospatial prediction models  
- Docker/deploy verification as “production ready” claim  
- Independent accuracy benchmarks  
