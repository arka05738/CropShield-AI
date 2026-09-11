# Hugging Face Model Comparison — CropShield AI (SIH 2026)

**Date:** 2026-09-11  
**Rule:** Classes and crops listed as VERIFIED only when confirmed from Hub `config.json` / published class lists in the repo. Card marketing claims alone are insufficient.

---

## Comparison table

| Model | Architecture | Dataset | Crops (verified) | Classes | Accuracy/Metric | Size | Inference | License | Deployment | Recommendation |
|-------|--------------|---------|------------------|---------|-----------------|------|-----------|---------|------------|----------------|
| `kimcomehome/plantvillage-vit-leaf-disease` | ViT-B/16 (`ViTForImageClassification`) | PlantVillage | Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato (**VERIFIED** `id2label`) | 38 | Card: Acc 0.9979 overall; Maize Acc 0.9844 / F1 0.9785 (**card-reported**, not re-benchmarked here) | 85.8M | `transformers` pipeline, 224² | Check Hub card | CPU feasible; Hub download ~hundreds MB | **BEST for PlantVillage crops already in SIH (Grape, Tomato, Potato, Maize)** |
| `DScomp380/vit-b16-plant_village` | ViT-B/16 | Treelar/plant_village | Same PlantVillage family + `Background_without_leaves` (**VERIFIED** 39 labels) | 39 | Eval Acc **0.9973** (card training log) | 85.8M | transformers | Check Hub | Same as above | Strong alternate; includes background class |
| `VaigandlaHemanth/leaf-disease-clip-vit` | CLIP ViT-B/32 + clf head | PlantVillage | Same 14-crop PlantVillage set (**VERIFIED** `id2label`) | 38 | Card: expected >95% (**UNVERIFIED** hard number) | CLIP-scale | transformers (CLIP) | Check Hub | Needs newer transformers; heavier | Prefer standard ViT unless CLIP needed |
| `wambugu71/crop_leaf_diseases_vit` | ViT-Tiny | Custom multi-crop | Corn, Potato, Rice, Wheat + Invalid (**VERIFIED**) | 13 | **UNVERIFIED** (no metrics in config) | Tiny (~5–22M class) | transformers | Check Hub | Light for Render | **BEST verified HF path for Rice + Wheat** (narrow) |
| `LishaV01/agriculture-crop-disease-detection` | ViT-Tiny | Card: multi-crop | Corn, Potato, Rice, Wheat, Sugarcane (**VERIFIED** `id2label` 20 labels) | 20 | **UNVERIFIED** metrics | Tiny | transformers | Check Hub | Light | **Candidate for Sugarcane + Rice/Wheat**; needs own smoke test before production |
| `Giftmutie/agriculture-crop-disease-detection` | Card: ViT+LoRA | Same family as Lisha | Card claims Sugarcane… (**config not independently re-fetched**; treat as **sibling UNVERIFIED** until config checked) | UNVERIFIED | UNVERIFIED | 5.53M (card) | transformers? | Check Hub | Light | Do not select until config verified |
| `rmezapi/sugarcane-diagnosis-swin-tiny` | Swin-Tiny | Sugarcane leaf dataset | Sugarcane only (card) | 5 | Card ~97% test | 27.6M | transformers | Check Hub | Light | **NOT READY:** Hub `id2label` is `LABEL_0`…`LABEL_4` only — disease names **not verified in config** |
| `dwililiya/sugarcane-plant-diseases-classification` | EfficientNet (card) | Kaggle sugarcane (6 classes) | Sugarcane (card) | 6 (card) | Test Acc 0.8683 (card) | UNVERIFIED | **Likely non-transformers** | CDLA-Sharing-1.0 (card) | Integration friction | Prefer transformers-native models |
| `Arko007/nfnet-f1-plant-disease` | NFNet-F1 (`timm`) | Multi-crop real-world | Apple, Cassava, Cherry, Chili, Coffee, Corn, Cucumber, Guava, Grape, Jamun, Lemon, Mango, Peach, Pepper, Pomegranate, Potato, **Rice**, Soybean, Strawberry, **Sugarcane**, Tea, Tomato, **Wheat** (**VERIFIED** `class_names`) — **NO Cotton, NO Sunflower** | 88 | Val Acc **0.954**, F1 **0.886** (`metrics.json` VERIFIED) | ~130M | **timm + safetensors**, 512² | Check Hub | **Heavy for Render free** (RAM, CPU latency) | Strong multi-crop coverage; requires `timm` stack, not current pipeline |
| Cotton-specific HF transformers model | — | — | — | — | — | — | — | — | — | **NO VERIFIED MODEL FOUND** |
| Sunflower-specific HF transformers model | — | Dataset only: `Project-AgML/sunflower_disease_classification` | Downy_mildew, Fresh_leaf, Gray_mold, Leaf_scars (dataset) | 4 | N/A (dataset) | N/A | N/A | — | — | **NO VERIFIED MODEL FOUND** |

---

## BEST OVERALL MODEL (for current FastAPI + transformers stack)

**`kimcomehome/plantvillage-vit-leaf-disease`** — verified labels, honest card limitations, pipeline-native, already wired.

**Not** best overall for the full SIH crop list (Sugarcane/Cotton/Sunflower).

---

## BEST MODEL FOR EACH SUPPORTED / TARGET CROP

| Crop | Best verified candidate | Status |
|------|-------------------------|--------|
| Grape | `kimcomehome/plantvillage-vit-leaf-disease` | VERIFIED classes |
| Tomato | same | VERIFIED |
| Potato | same **or** `wambugu71/...` (fewer potato classes) | VERIFIED |
| Maize/Corn | PlantVillage ViT **or** `wambugu71` / `LishaV01` | VERIFIED |
| Rice | `wambugu71/crop_leaf_diseases_vit` or `LishaV01/...` | VERIFIED labels; metrics UNVERIFIED |
| Wheat | same | VERIFIED labels; metrics UNVERIFIED |
| Sugarcane | `LishaV01/...` (3 classes) **or** future Swin after label map fix; alt `Arko007` (timm) | Partial VERIFIED labels; **metrics/smoke UNVERIFIED** |
| Cotton | — | **NO VERIFIED MODEL FOUND** |
| Sunflower | — | **NO VERIFIED MODEL FOUND** |

---

## MODELS THAT SHOULD NOT BE USED (yet)

| Model | Reason |
|-------|--------|
| `rmezapi/sugarcane-diagnosis-swin-tiny` | Opaque `LABEL_0`…`LABEL_4` in config |
| Any PlantVillage model as sole SIH disease engine | Missing Sugarcane/Cotton/Sunflower/Rice/Wheat |
| Old local `.keras` DenseNet outside this repo | Explicitly disallowed; not HF primary |
| Heuristic necrosis classifier as “AI diagnosis” | Fabricates disease names |
| `dwililiya/...` until transformers-compatible loader proven | Framework mismatch risk |
| `Arko007` on Render free without capacity proof | 130M + 512² + timm |

---

## CROPS STILL WITHOUT VERIFIED MODEL SUPPORT

1. **Cotton** — NO VERIFIED MODEL FOUND  
2. **Sunflower** — NO VERIFIED MODEL FOUND  
3. **Sugarcane** — candidate labels exist (`LishaV01`, `Arko007`) but **production integration deferred** until smoke inference + registry design approved  

---

## Proposed multi-model registry (FUTURE — not implemented)

| Env var | Intended model | Gate |
|---------|----------------|------|
| `HF_MODEL_DEFAULT_PLANTVILLAGE` | `kimcomehome/plantvillage-vit-leaf-disease` | Grape, Tomato, Potato, Maize, … |
| `HF_MODEL_RICE_WHEAT` | `wambugu71/crop_leaf_diseases_vit` | Rice, Wheat (+ Corn/Potato overlap) |
| `HF_MODEL_SUGARCANE` | TBD after smoke (`LishaV01` or fixed Swin) | Sugarcane only |
| `HF_MODEL_COTTON` | — | Empty until verified |
| `HF_MODEL_SUNFLOWER` | — | Empty until verified |

---

## Decision

**STOP major multi-model architectural integration.**  

Evidence is sufficient to keep PlantVillage ViT for covered crops and to **refuse** unsupported crops honestly. Evidence is **insufficient** to declare a production multi-model registry for all SIH targets without real inference verification.
