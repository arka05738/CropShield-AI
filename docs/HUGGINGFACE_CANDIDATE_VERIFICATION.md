# Hugging Face Candidate Verification

**Date:** 2026-09-11  
**Scope:** Config inspection + **real model download/load/inference** for SIH candidates.  
**Production API / registry:** **NOT changed** (STOP after this report).  
**Script (isolated):** `Backend/scripts/verify_hf_candidates.py`  
**Raw machine log:** `docs/_hf_candidate_verify_raw.json`

**Input used for smoke inference:** synthetic 224×224 leaf-like JPEG  
(`Backend/data/_hf_verify_samples/synthetic_leaf.jpg`).  
This proves **MODEL LOADED** + **REAL INFERENCE** executed. It does **not** validate diagnostic accuracy on field disease images.

Verification levels used below:

| Level | Meaning |
|-------|---------|
| CONFIG VERIFIED | Hub `config.json` / `class_names` / `id2label` inspected |
| MODEL LOADED | Weights downloaded and instantiated successfully |
| REAL INFERENCE VERIFIED | Forward pass produced label + softmax confidence |

Allowed status vocabulary in §5: **VERIFIED** | **UNVERIFIED** | **NOT SUPPORTED** | **FAILED**

---

## 1. Current Model

**Model:** `kimcomehome/plantvillage-vit-leaf-disease`  
**Architecture:** `ViTForImageClassification` (ViT-Base, ImageNet-21k fine-tune lineage)  
**Dataset (card):** PlantVillage (`BrandonFors/Plant-Diseases-PlantVillage-Dataset` on card)  
**License (Hub):** `cc-by-sa-3.0`  
**Framework:** `transformers` + `safetensors` (`model.safetensors`)  
**Size:** ~85.8M params (F32)  
**Preprocess:** Hub `preprocessor_config.json`; 224×224 via `AutoImageProcessor`  
**Params loaded:** 85,827,878  

### Verified labels (`id2label`, CONFIG VERIFIED — 38)

1. Apple___Apple_scab  
2. Apple___Black_rot  
3. Apple___Cedar_apple_rust  
4. Apple___healthy  
5. Blueberry___healthy  
6. Cherry_(including_sour)___Powdery_mildew  
7. Cherry_(including_sour)___healthy  
8. Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot  
9. Corn_(maize)___Common_rust_  
10. Corn_(maize)___Northern_Leaf_Blight  
11. Corn_(maize)___healthy  
12. Grape___Black_rot  
13. Grape___Esca_(Black_Measles)  
14. Grape___Leaf_blight_(Isariopsis_Leaf_Spot)  
15. Grape___healthy  
16. Orange___Haunglongbing_(Citrus_greening)  
17. Peach___Bacterial_spot  
18. Peach___healthy  
19. Pepper,_bell___Bacterial_spot  
20. Pepper,_bell___healthy  
21. Potato___Early_blight  
22. Potato___Late_blight  
23. Potato___healthy  
24. Raspberry___healthy  
25. Soybean___healthy  
26. Squash___Powdery_mildew  
27. Strawberry___Leaf_scorch  
28. Strawberry___healthy  
29. Tomato___Bacterial_spot  
30. Tomato___Early_blight  
31. Tomato___Late_blight  
32. Tomato___Leaf_Mold  
33. Tomato___Septoria_leaf_spot  
34. Tomato___Spider_mites Two-spotted_spider_mite  
35. Tomato___Target_Spot  
36. Tomato___Tomato_Yellow_Leaf_Curl_Virus  
37. Tomato___Tomato_mosaic_virus  
38. Tomato___healthy  

**Target-crop support from labels only:**

| Crop | Status |
|------|--------|
| Grape | **SUPPORTED** |
| Sugarcane | **NOT SUPPORTED** |
| Rice | **NOT SUPPORTED** |
| Wheat | **NOT SUPPORTED** |
| Cotton | **NOT SUPPORTED** |
| Sunflower | **NOT SUPPORTED** |

### Real inference (synthetic leaf)

| Field | Value |
|-------|--------|
| Predicted label | `Soybean___healthy` |
| Confidence | **0.087190** (low — expected on non-real leaf) |
| Top-3 | Soybean___healthy 0.087; Tomato___Late_blight 0.054; Orange___HLB 0.052 |
| Load time | ~104.3 s (cold download) |
| Infer time | ~0.77 s CPU |
| Status | **PASS** |

**Status summary:** CONFIG VERIFIED · MODEL LOADED · REAL INFERENCE VERIFIED  

**Card metrics (not re-benchmarked here):** overall Acc ≈ 0.9979; maize Acc 0.9844 / F1 0.9785 (model card).

---

## 2. Sugarcane Candidate

### Primary transformers-native candidate

**Exact model ID:** `LishaV01/agriculture-crop-disease-detection`  
**Architecture:** `ViTForImageClassification` (ViT-Tiny base `WinKawaks/vit-tiny-patch16-224`)  
**Dataset:** Card says RGB images of Sugarcane/Corn/Potato/Rice/Wheat — **no public dataset name / split metrics in card** → dataset details **UNVERIFIED** beyond card text  
**License:** `apache-2.0`  
**Framework:** `transformers` + `safetensors`  
**Size:** ~5.53M params  
**Evidence:** Hub `config.json` `id2label` (CONFIG VERIFIED) + successful load/inference  

### Sugarcane labels (exact strings from config)

1. `sugarcane_Bacterial Blight`  
2. `sugarcane_Healthy`  
3. `sugarcane_Red Rot`  

**Sugarcane crop status:** **SUPPORTED** (3 verified classes)

### Full model classes (20) — CONFIG VERIFIED

```
0 Corn___Common_Rust
1 Corn___Gray_Leaf_Spot
2 Corn___Healthy
3 Invalid
4 Potato___Early_Blight
5 Potato___Healthy
6 Potato___Late_Blight
7 Rice___Brown_Spot
8 Rice___Healthy
9 Rice___Leaf_Blast
10 Wheat___Brown_Rust
11 Wheat___Healthy
12 Wheat___Yellow_Rust
13 Rice_Bacterial Blight Disease
14 Rice_Blast Disease
15 Rice_Brown Spot Disease
16 Rice_False Smut Disease
17 sugarcane_Bacterial Blight
18 sugarcane_Healthy
19 sugarcane_Red Rot
```

**Note:** README also lists “Corn Leaf Blight”; that string is **not** in `id2label` → treat Corn Leaf Blight as **NOT SUPPORTED** by config.

### Model loading / real inference

| Field | Value |
|-------|--------|
| MODEL LOADED | Yes (~11.5 s) |
| REAL INFERENCE | **PASS** |
| Predicted label | `Rice_Brown Spot Disease` |
| Confidence | **0.986276** (on synthetic image — **not** a disease accuracy claim) |
| Params | 5,528,276 |

**Status:** CONFIG VERIFIED · MODEL LOADED · REAL INFERENCE VERIFIED  
**Recommendation:** **Best transformers-native Sugarcane candidate** for a future limited registry (3 classes only). Accuracy vs field sugarcane images: **UNVERIFIED**.

### Alternate Sugarcane-capable model

**Exact model ID:** `Arko007/nfnet-f1-plant-disease`  
**Architecture:** `nfnet_f1` via **timm** (not `transformers` AutoModel)  
**Sugarcane labels (CONFIG VERIFIED):**

1. `Sugarcane__bacterial_blight`  
2. `Sugarcane__healthy`  
3. `Sugarcane__red_rot`  
4. `Sugarcane__red_stripe`  
5. `Sugarcane__rust`  

| Field | Value |
|-------|--------|
| MODEL LOADED | Yes (~202 s cold) |
| REAL INFERENCE | **PASS** |
| Predicted | `Sugarcane__red_rot` |
| Confidence | **0.927360** (synthetic — not accuracy claim) |
| Params | 129,831,656 |
| Input size | 512×512 |
| License | **cc-by-nc-sa-4.0** (non-commercial — SIH/commercial risk) |
| metrics.json | val_accuracy **0.95397**, val_f1 **0.88601** (Hub file) |

**Recommendation:** Stronger sugarcane class count, but **heavier**, **non-transformers**, and **NC license**. Prefer only if license is acceptable and Render capacity proven.

---

## 3. Rice Candidate

### Candidate A — `wambugu71/crop_leaf_diseases_vit`

**Architecture:** `ViTForImageClassification` (ViT-Tiny)  
**License:** `mit` (Hub tags; README also mentions Apache 2.0 — Hub tag is MIT)  
**Dataset:** Card: public + private multi-crop; exact corpus **UNVERIFIED**  
**Card metrics (source = model card only):** Accuracy 98%, Precision 97%, Recall 97%, F1 96% — **not** reproduced here; **not** comparable to PlantVillage numbers.

**Rice labels (CONFIG VERIFIED):**

1. `Rice___Brown_Spot`  
2. `Rice___Healthy`  
3. `Rice___Leaf_Blast`  

README mentions Rice Hispa in training narrative; **Hispa is absent from `id2label`** → Hispa **NOT SUPPORTED** by config.

| Field | Value |
|-------|--------|
| MODEL LOADED | Yes (~10.8 s) |
| REAL INFERENCE | **PASS** |
| Predicted | `Rice___Leaf_Blast` |
| Confidence | **0.270815** |
| Params | 5,526,925 |

**Rice status:** **SUPPORTED** (3 classes)

### Candidate B — `LishaV01/agriculture-crop-disease-detection`

**Rice labels (CONFIG VERIFIED):**

1. `Rice___Brown_Spot`  
2. `Rice___Healthy`  
3. `Rice___Leaf_Blast`  
4. `Rice_Bacterial Blight Disease`  
5. `Rice_Blast Disease`  
6. `Rice_Brown Spot Disease`  
7. `Rice_False Smut Disease`  

**Rice status:** **SUPPORTED** (7 label strings; some naming overlap / possible redundancy — do not merge without dataset proof)

### Candidate C — `Arko007/nfnet-f1-plant-disease`

**Rice labels (CONFIG VERIFIED):**

1. `Rice__brown_spot`  
2. `Rice__healthy`  
3. `Rice__hispa`  
4. `Rice__leaf_blast`  
5. `Rice__neck_blast`  

**Rice status:** **SUPPORTED** (5 classes)

**Recommendation for Rice:** Prefer **`wambugu71/crop_leaf_diseases_vit`** or **`LishaV01/...`** for transformers stack. Lisha has more rice label strings; wambugu is simpler/MIT and already widely used on Spaces. **Do not claim which is more accurate** without a shared benchmark.

---

## 4. Wheat Candidate

### `wambugu71/crop_leaf_diseases_vit` — Wheat labels (CONFIG VERIFIED)

1. `Wheat___Brown_Rust`  
2. `Wheat___Healthy`  
3. `Wheat___Yellow_Rust`  

**Wheat:** **SUPPORTED** · MODEL LOADED · REAL INFERENCE VERIFIED (same run as Rice)

### `LishaV01/agriculture-crop-disease-detection` — Wheat labels (CONFIG VERIFIED)

1. `Wheat___Brown_Rust`  
2. `Wheat___Healthy`  
3. `Wheat___Yellow_Rust`  

**Wheat:** **SUPPORTED** · MODEL LOADED · REAL INFERENCE VERIFIED

### `Arko007/nfnet-f1-plant-disease` — Wheat labels (CONFIG VERIFIED)

1. `Wheat__brown_rust`  
2. `Wheat__healthy`  
3. `Wheat__septoria`  
4. `Wheat__yellow_rust`  

**Wheat:** **SUPPORTED** · MODEL LOADED · REAL INFERENCE VERIFIED

**Recommendation for Wheat:** Transformers: **`wambugu71/...` or `LishaV01/...`** (identical wheat class set). Arko adds `septoria` but brings timm + NC license + size.

---

## 5. Final Decision

| Crop | Model | Evidence | Real Inference | Status |
|------|-------|----------|----------------|--------|
| Grape | `kimcomehome/plantvillage-vit-leaf-disease` | CONFIG `id2label` grape×4 | PASS (model smoke) | **VERIFIED** |
| Sugarcane | `LishaV01/agriculture-crop-disease-detection` | CONFIG sugarcane×3 | PASS | **VERIFIED** |
| Sugarcane (alt) | `Arko007/nfnet-f1-plant-disease` | CONFIG sugarcane×5 | PASS | **VERIFIED** (deploy/license caveats) |
| Rice | `wambugu71/crop_leaf_diseases_vit` | CONFIG rice×3 | PASS | **VERIFIED** |
| Rice (alt) | `LishaV01/...` / `Arko007/...` | CONFIG rice labels | PASS | **VERIFIED** |
| Wheat | `wambugu71/...` / `LishaV01/...` | CONFIG wheat×3 | PASS | **VERIFIED** |
| Wheat (alt) | `Arko007/...` | CONFIG wheat×4 | PASS | **VERIFIED** (caveats) |
| Cotton | — | No class strings in any verified candidate | — | **NOT SUPPORTED** |
| Sunflower | — | No class strings in any verified candidate | — | **NOT SUPPORTED** |
| PlantVillage for Sugarcane/Rice/Wheat | `kimcomehome/...` | Empty crop hits in config | N/A | **NOT SUPPORTED** |

---

## Accuracy claims (source/context only)

| Model | Metric | Source | Comparable across models? |
|-------|--------|--------|---------------------------|
| kimcomehome | Acc ~0.9979 (overall), maize Acc 0.9844 | Model card | **No** — PlantVillage lab domain |
| wambugu71 | Acc 98% / F1 96% | Model card | **No** — different data |
| LishaV01 | None found in card/config | — | **UNVERIFIED** |
| Arko007 | val Acc 0.954 / F1 0.886 | `metrics.json` on Hub | **No** — 88-class real-world mix |

Smoke confidences on synthetic leaves are **not** accuracy.

---

## Ready for multi-model registry?

**No — not for full SIH crop coverage.**

- **Ready to design (after your review):** limited registry mapping  
  - PlantVillage crops → `kimcomehome/...`  
  - Rice/Wheat → `wambugu71/...` **or** `LishaV01/...`  
  - Sugarcane → `LishaV01/...` (or Arko007 if license/RAM OK)  
- **Not ready:** Cotton, Sunflower (still **NOT SUPPORTED**)  
- **Not claimed ready** merely because `USE_MOCK_AI` pytest passes  

**STOP.** Awaiting your review before any registry implementation.
