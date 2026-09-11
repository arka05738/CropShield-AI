# Cotton & Sunflower Hugging Face Research

**Date:** 2026-09-11  
**Scope:** Research + config verification + real load/inference only.  
**Production registry:** **NOT modified** (STOP before integration).  
**Isolated script:** `Backend/scripts/verify_hf_cotton_sunflower.py`  
**Raw log:** `docs/_hf_cotton_sunflower_verify_raw.json`  
**Smoke image:** synthetic leaf JPEG — **SMOKE TEST ONLY** (confidence ≠ accuracy).

---

## Search summary

Hub searches (`image-classification` + cotton/sunflower keywords) found few usable Transformers models. Most hits were:

- Keras/H5 weights  
- Empty repos  
- Pest-only classifiers  
- VLMs (Qwen2.5-VL) unsuitable for current FastAPI ViT path  
- Datasets without published models  

Known multi-crop model `Arko007/nfnet-f1-plant-disease` was previously verified: **no Cotton / no Sunflower** in `class_names`.

---

# Cotton Models

## 1. YaswanthReddy23/ViT_Cotton — **best disease candidate**

| Field | Evidence |
|-------|----------|
| **Model ID** | `YaswanthReddy23/ViT_Cotton` |
| **Architecture** | `ViTForImageClassification` (base `google/vit-base-patch16-224-in21k`) |
| **Framework** | `transformers` + `safetensors` + `preprocessor_config.json` |
| **Dataset** | Card: **“unknown dataset”** → dataset name **UNVERIFIED**. Class names **exactly match** SAR-CLD-2024 / `Project-AgML/cotton_leaf_disease_classification_bangladesh_2` class set (Bacterial Blight, Curl Virus, Healthy Leaf, Herbicide Growth Damage, Leaf Hopper Jassids, Leaf Redding, Leaf Variegation). |
| **Labels (CONFIG VERIFIED)** | See list below |
| **Cotton labels** | All 7 classes are cotton leaf conditions. **Note:** label strings do **not** contain the token `Cotton` / `cotton` (unlike `sugarcane_*`). Crop routing must use `crop_hint=Cotton`, not substring filter on `"cotton"`. |
| **Metrics** | Card eval Acc **0.9859**, Loss 0.0678 (training log). Source = model card only → treat as **VERIFIED card metric**, not our benchmark. |
| **License** | **apache-2.0** (Hub) — no NC restriction found |
| **Model size** | ~85.8M params (F32) |
| **Load** | **PASS** (~110.7 s cold download/load) |
| **Real inference** | **PASS** (SMOKE TEST ONLY) |
| **Predicted / conf** | `Healthy Leaf` / **0.282714** |
| **Inference time** | ~0.43 s CPU |
| **Deployment** | Same class as PlantVillage ViT-B; practical on Render paid; adds another ~86M model to cache |
| **Recommendation** | **VERIFIED — suitable candidate** for future Cotton disease routing (pending your approval). Not pest-only. |

### Exact Cotton labels (`id2label`)

1. Bacterial Blight  
2. Curl Virus  
3. Healthy Leaf  
4. Herbicide Growth Damage  
5. Leaf Hopper Jassids  
6. Leaf Redding  
7. Leaf Variegation  

---

## 2. ashishp-wiai/vit-base-patch16-224-in21k-finetuned-CottonPestClassification_v3a_os

| Field | Evidence |
|-------|----------|
| **Model ID** | `ashishp-wiai/vit-base-patch16-224-in21k-finetuned-CottonPestClassification_v3a_os` |
| **Architecture** | ViT image classification |
| **Labels (CONFIG VERIFIED)** | `aphids`, `none`, `whitefly` |
| **Cotton labels** | Pest/absence only — **not disease classes** |
| **Metrics** | **NOT AVAILABLE** in inspected config |
| **License** | **UNVERIFIED** / missing on Hub card |
| **Load / inference** | **PASS** / **PASS** (smoke: `none` @ 0.382) |
| **Recommendation** | **Not for disease registry** (pest triage only). Could be FUTURE pest module. |

---

## 3. RohithN2004/Cotton-pests

| Field | Evidence |
|-------|----------|
| **Model ID** | `RohithN2004/Cotton-pests` |
| **Architecture** | ViT (config) |
| **Labels (CONFIG VERIFIED)** | American Bollworm; Cotton Aphid; Pink; Red Cotton Bug; Spotted Bollworm; Thrips; Whitefly |
| **Cotton labels** | Pest names (some include “Cotton”) — **not foliar diseases** |
| **Metrics** | **NOT AVAILABLE** |
| **License** | **UNVERIFIED** / missing |
| **Load** | **FAILED** — `AutoImageProcessor` unrecognized (`preprocessor_config.json` incompatible with current transformers) |
| **Recommendation** | **Do not use** for disease path; processor broken for our stack. |

---

## 4. Other Cotton finds (not loaded as production candidates)

| Model ID | Why rejected / limited |
|----------|-------------------------|
| `varun2k4/Cotton_Disease_Detection` | Keras `best_model.keras` only; not Transformers |
| `aleisya01/cotton-leaf-diseases-and-pest-detection` | `.h5` only; empty metadata |
| `Rugs25/Cotton_Disease_Detection` | `.h5` only |
| `hen8001/cotton_crop_identification` | Keras; crop ID not disease |
| `beverlyhillscop/cotton-disease-qwen25vl-*` | Vision-language model; wrong stack / heavy |
| `Arko007/nfnet-f1-plant-disease` | Prior audit: **no cotton classes** |

---

# Sunflower Models

## 1. YaswanthReddy23/ViT_Sunflower — **best disease candidate**

| Field | Evidence |
|-------|----------|
| **Model ID** | `YaswanthReddy23/ViT_Sunflower` |
| **Architecture** | `ViTForImageClassification` (`google/vit-base-patch16-224-in21k`) |
| **Framework** | `transformers` + `safetensors` |
| **Dataset** | Card: **“unknown dataset”** → name **UNVERIFIED**. Labels align with `Project-AgML/sunflower_disease_classification` (Downy_mildew, Gray_mold, Leaf_scars, Fresh_leaf≈Healthy). |
| **Labels (CONFIG VERIFIED)** | Downy mildew; Gray mold; Healthy; Leaf scars |
| **Sunflower labels** | All 4 classes are sunflower conditions. Token `sunflower` **not** in label strings → route via `crop_hint=Sunflower`. |
| **Metrics** | Card training table Acc **0.9709**. Repo also has `eval_results.json` with `eval_accuracy` **0.381** (conflicting artifact — possibly non-best checkpoint). Treat card Acc as **VERIFIED card claim**; treat `eval_results.json` as **UNVERIFIED / conflicting**. Do **not** treat either as our benchmark. |
| **License** | **apache-2.0** |
| **Model size** | ~85.8M params |
| **Load** | **PASS** (~106.9 s cold) |
| **Real inference** | **PASS** (SMOKE TEST ONLY) |
| **Predicted / conf** | `Gray mold` / **0.392348** |
| **Inference time** | ~0.34 s CPU |
| **Deployment** | Same ViT-B footprint as PlantVillage / Cotton candidate |
| **Recommendation** | **VERIFIED — suitable candidate** for future Sunflower routing (pending approval). Resolve metrics conflict before marketing accuracy. |

### Exact Sunflower labels (`id2label`)

1. Downy mildew  
2. Gray mold  
3. Healthy  
4. Leaf scars  

---

## 2. Other Sunflower finds

| Model ID | Status |
|----------|--------|
| `tariqul/sunflowerDiseaseClassification` | Repo essentially empty (`.gitattributes` only) → **NOT FOUND** usable weights |
| `tariqul/swin-finetuned-sunflowerDisease` | Empty → **NOT FOUND** |
| `karannnn309/sunflower-disease-classifier` | Only `sunflower_disease_model.pth` — no Transformers config/`id2label` → **UNVERIFIED** (not loaded) |
| PlantVillage family models | **No sunflower classes** |

---

# Final Decision

| Crop | Model | Verified Labels | Real Load | Real Inference | Metrics | License | Recommendation |
|------|-------|-----------------|-----------|----------------|---------|---------|----------------|
| Cotton (disease) | `YaswanthReddy23/ViT_Cotton` | Yes (7 classes; no `cotton` token in names) | PASS | PASS (smoke) | Card Acc 0.9859 | apache-2.0 | **VERIFIED — suitable candidate** |
| Cotton (pest) | `ashishp-wiai/...CottonPest...` | Pest-only (3) | PASS | PASS (smoke) | NOT AVAILABLE | UNVERIFIED | Not for disease registry |
| Cotton (pest) | `RohithN2004/Cotton-pests` | Pest labels | FAILED | FAILED | NOT AVAILABLE | UNVERIFIED | Reject (processor) |
| Sunflower | `YaswanthReddy23/ViT_Sunflower` | Yes (4 classes; no `sunflower` token) | PASS | PASS (smoke) | Card Acc 0.9709; conflicting eval JSON | apache-2.0 | **VERIFIED — suitable candidate** |
| Sunflower | Empty / `.pth` only repos | — | — | — | — | — | **NOT FOUND** / UNVERIFIED |

### Status vocabulary

- **Cotton disease:** **VERIFIED — suitable candidate** (`YaswanthReddy23/ViT_Cotton`) — **INTEGRATED into production registry (2026-09-11)**  
- **Sunflower disease:** **VERIFIED — suitable candidate** (`YaswanthReddy23/ViT_Sunflower`) — **INTEGRATED into production registry (2026-09-11)**  

### Sunflower metric conflict (project policy)

Evaluation metric conflict identified in the Hugging Face repository (model card Acc ≈ 0.9709 vs `eval_results.json` Acc ≈ 0.38). The model has successful real inference, but the reported evaluation metrics are inconsistent; **therefore no accuracy figure is claimed for this model in the project.**

**MODEL-CARD METRIC ≠ OUR SYSTEM ACCURACY.**

### Production action

Cotton and Sunflower routes added to `hf_crop_registry.py` after approval. Specialist models use empty `crop_filter_tokens` (labels omit crop name).
