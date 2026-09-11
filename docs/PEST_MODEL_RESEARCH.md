# Pest Model Research

**Date:** 2026-09-11  
**Scope:** Research + real Hugging Face load/inference verification only  
**Not in scope:** Pest production integration, disease AI changes, frontend, RAG, DB schema, API changes

**Desired CropShield pest output:** image → pest name → bounding box → confidence → detection count  
⇒ **Object detection preferred** over whole-image classification.

**Evidence artifacts (local research only):** `docs/_pest_research/verification_results.json`, `docs/_pest_research/samba_extra.json`  
**Runtime:** isolated venv `docs/_pest_research_venv` (Ultralytics 8.4.146, torch 2.14.0+cpu) — **not** added to production requirements.

---

## Candidate 1

**Model:** `underdogquality/yolo11s-pest-detection`  
**Architecture:** Ultralytics YOLO11 Small (object detection head)  
**Task:** Object detection  
**Dataset:** IP102 (card: “Balanced, 34K+ images”; IP102 paper: ~75K classification images / ~19K detection boxes). Card cites training 640×640 and 896×896, 77 epochs, A100.  
**Classes (102 — from repo `pests.yaml`, not inferred from name):**

rice leaf roller; rice leaf caterpillar; paddy stem maggot; asiatic rice borer; yellow rice borer; rice gall midge; Rice Stemfly; brown plant hopper; white backed plant hopper; small brown plant hopper; rice water weevil; rice leafhopper; grain spreader thrips; rice shell pest; grub; mole cricket; wireworm; white margined moth; black cutworm; large cutworm; yellow cutworm; red spider; corn borer; army worm; aphids; Potosiabre vitarsis; peach borer; english grain aphid; green bug; bird cherry-oataphid; wheat blossom midge; penthaleus major; longlegged spider mite; wheat phloeothrips; wheat sawfly; cerodonta denticornis; beet fly; flea beetle; cabbage army worm; beet army worm; Beet spot flies; meadow moth; beet weevil; sericaorient alismots chulsky; alfalfa weevil; flax budworm; alfalfa plant bug; tarnished plant bug; Locustoidea; lytta polita; legume blister beetle; blister beetle; therioaphis maculata Buckton; odontothrips loti; Thrips; alfalfa seed chalcid; Pieris canidia; Apolygus lucorum; Limacodidae; Viteus vitifoliae; Colomerus vitis; Brevipoalpus lewisi McGregor; oides decempunctata; Polyphagotars onemus latus; Pseudococcus comstocki Kuwana; parathrene regalis; Ampelophaga; Lycorma delicatula; Xylotrechus; Cicadella viridis; Miridae; Trialeurodes vaporariorum; Erythroneura apicalis; Papilio xuthus; Panonchus citri McGregor; Phyllocoptes oleiverus ashmead; Icerya purchasi Maskell; Unaspis yanonensis; Ceroplastes rubens; Chrysomphalus aonidum; Parlatoria zizyphus Lucus; Nipaecoccus vastalor; Aleurocanthus spiniferus; Tetradacus c Bactrocera minax; Dacus dorsalis(Hendel); Bactrocera tsuneonis; Prodenia litura; Adristyrannus; Phyllocnistis citrella Stainton; Toxoptera citricidus; Toxoptera aurantii; Aphis citricola Vander Goot; Scirtothrips dorsalis Hood; Dasineura sp; Lawana imitata Melichar; Salurnis marginella Guerr; Deporaus marginatus Pascoe; Chlumetia transversa; Mango flat beak leafhopper; Rhytidodera bowrinii white; Sternochetus frigidus; Cicadellidae

**Metrics (author-reported on IP102; not CropShield metrics):**

| Split | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|-------|-----------|--------|---------|--------------|
| Train (card table) | 0.912 | 0.923 | 0.941 | 0.838 |
| Validation (card table) | 0.744 | 0.789 | 0.815 | 0.605 |
| HF model-index (self-reported, unverified) | 0.923 | 0.907 | 0.941 | 0.838 |

**Note:** HF model-index numbers align with **train** (or mixed) claims more than the card’s **validation** row — treat train numbers as optimistic.

**License:** MIT (repo `LICENSE` / card). **Dataset caveat:** IP102 authors state dataset is free for **academic** use; other purposes require contacting the authors — commercial product use of IP102-derived models needs legal review.  
**Framework:** Ultralytics / PyTorch `.pt` (`best.pt` ≈ **38.3 MB**)  
**Preprocessing:** Ultralytics default letterbox resize to `imgsz=640` (verified in predict calls)  
**Maintenance:** Created 2025-04; lastModified 2025-04-29; ~243 downloads/month; Spaces exist  
**CPU:** Feasible (verified below)  
**Deployment:** Strong fit for broad pest OD; adds `ultralytics` dependency (library AGPL-3.0 — separate from model MIT)

**Suitability scores (1–10) with evidence:**

| Category | Score | Evidence |
|----------|-------|----------|
| Broad pest coverage | **9** | Exact 102 IP102 names in `pests.yaml` |
| Field-image relevance | **7** | IP102 includes field/crop pests; long-tail / imbalance known from CVPR paper |
| Dataset quality | **7** | CVPR 2019 benchmark; detection subset ~19K boxes; “balanced 34K+” claim not independently re-verified |
| Evaluation evidence | **6** | Card publishes val mAP; HF index appears train-skewed; no third-party verify |
| Detection capability | **9** | True OD with boxes (task + Detect head in weights) |
| Model size | **9** | ~38 MB weights |
| CPU feasibility | **8** | Real CPU infer ~4.1 s cold / workable warm |
| License | **6** | Model MIT OK; IP102 academic restriction + Ultralytics AGPL dep risk |
| Deployment risk | **6** | New stack vs current transformers ViT disease path; AGPL dependency |

**Real load:** **PASS** (102 classes loaded from weights)  
**Real inference:** **PASS** on SambaGuard FAW collage/training mosaic → **0 detections** (out-of-domain collage; pipeline OK). Smoke follow-up at conf 0.05: not used as accuracy.  
**Inference time:** ~4066 ms CPU (first call includes warmup)  
**Deployment:** Good primary candidate for CropShield OD goals  
**Decision:** **PRIMARY recommendation** (broad OD)

---

## Candidate 2

**Model:** `Mustafa5645344/insect-detection-yolov8` *(additional strong candidate)*  
**Architecture:** Ultralytics YOLOv8**m**  
**Task:** Object detection  
**Dataset:** Roboflow `specifly-3-rwm7i` / Specifly (~49,680 augmented agricultural insect images, 21 taxa)  
**Classes (21 — loaded from weights `model.names`):**

`ant`, `aphid`, `bees`, `butterfly`, `caterpillar`, `cicada`, `dragonfly`, `grasshopper`, `green_lacewing`, `ladybug`, `leafhopper`, `mantis`, `mole_cricket`, `planthopper`, `rhino_beetle`, `rice_bug`, `spider`, `stem_borer`, `stink_bug`, `undefined`, `weevil`

**Metrics (author-reported validation; not CropShield):**

- Overall val: Precision **0.835**, Recall **0.816**, mAP@50 **0.854**, mAP@50-95 **0.519** (2,987 images / 3,097 instances)
- Peak claims: mAP@50 **0.8572**, Precision **0.8346**, Recall **0.8586**, F1 **0.824**
- Params: **23.23M**, GFLOPs **67.9**; A100 infer claim 1.5 ms (GPU — not our CPU)

**License:** Card **MIT**. Checkpoint metadata embeds Ultralytics string `AGPL-3.0 (https://ultralytics.com/license)` — **flag for legal review** (HF MIT vs Ultralytics AGPL ecosystem).  
**Framework:** Ultralytics YOLOv8.3.0; `best.pt` ≈ **46.8 MB**  
**Preprocessing:** imgsz 640  
**Maintenance:** Created 2026-08-21; low downloads (~50)  
**CPU:** Feasible  
**Deployment:** Smaller class set; includes beneficials (`bees`, `ladybug`) and `undefined` — useful but less India multi-crop species granularity than IP102

**Suitability scores:**

| Category | Score | Evidence |
|----------|-------|----------|
| Broad pest coverage | **5** | 21 coarse taxa; not fine-grained IP102 species |
| Field-image relevance | **7** | Explicit field/greenhouse agricultural dataset |
| Dataset quality | **6** | Large augmented Roboflow set; augmentation can inflate metrics |
| Evaluation evidence | **7** | Detailed per-class val table published |
| Detection capability | **9** | Real OD |
| Model size | **7** | ~47 MB but YOLOv8m heavier compute than YOLO11s |
| CPU feasibility | **7** | ~0.7 s CPU on mosaic after load |
| License | **5** | Card MIT vs AGPL string in `.pt` — uncertainty |
| Deployment risk | **6** | Heavier than YOLO11s; AGPL flag |

**Real load:** **PASS** (21 classes)  
**Real inference:** **PASS**; 0 dets on FAW mosaics (domain mismatch).  
**Inference time:** ~723 ms CPU  
**Decision:** **BACKUP** (stronger published val mAP, fewer/coarser classes)

---

## Candidate 3

**Model:** `ndunge23/SambaGuard-v2`  
**Architecture:** YOLOv8s (11.1M params, 28.4 GFLOPs)  
**Task:** Object detection  
**Dataset:** Cleaned KaraAgro AI Maize (Harvard Dataverse DOI 10.7910/DVN/CXUMDS, **CC0 1.0** source); train 5709 / val 1320 / test 664  
**Classes (4 — from card + loaded weights):**

| ID | Name |
|----|------|
| 0 | fall armyworm egg |
| 1 | fall armyworm frass |
| 2 | fall armyworm larva |
| 3 | fall armyworm larval damage |

**Metrics (validation; author-reported; not CropShield):**

- Overall: P **0.479**, R **0.376**, mAP50 **0.347**, mAP50-95 **0.137**
- Best class: larva mAP50 **0.726**
- Best checkpoint epoch 55 / 100

**License:** **Apache-2.0** (card) — commercial-friendly; attribution required  
**Framework:** Ultralytics; `weights/best.pt` (+ onnx/tflite present)  
**Maintenance:** Active 2026 (lastModified 2026-09-06)  
**CPU:** Strong (edge/RPi design goal)  
**Deployment:** Excellent specialist; **too narrow** as sole CropShield pest model

**Suitability scores:**

| Category | Score | Evidence |
|----------|-------|----------|
| Broad pest coverage | **2** | FAW-only (4 stage/symptom classes) |
| Field-image relevance | **8** | Smallholder maize FAW field imagery |
| Dataset quality | **7** | Documented cleaning; CC0 source |
| Evaluation evidence | **8** | Honest modest mAP + per-class tables + plots in repo |
| Detection capability | **8** | Real boxes; verified detections on training mosaic |
| Model size | **9** | YOLOv8s-class footprint |
| CPU feasibility | **9** | ~0.3–0.4 s CPU on mosaic |
| License | **9** | Apache-2.0 + CC0 dataset lineage |
| Deployment risk | **3** | Narrow scope if used alone |

**Real load:** **PASS** (4 classes)  
**Real inference:** **PASS** on `training_samples/train_batch0.jpg`:

| conf | # dets | Example |
|------|--------|---------|
| 0.25 | **2** | `fall armyworm larval damage` 0.368 @ `[1511.58, 1492.26, 1608.7, 1785.18]`; `fall armyworm frass` 0.266 @ `[148.34, 1025.77, 242.93, 1244.0]` |
| 0.10 | **6** | additional larval-damage boxes |

Inference time: **~404 ms** (conf 0.25), **~325 ms** (conf 0.10) CPU  

**Decision:** **SPECIALIST / optional secondary** — not primary (coverage)

---

## Candidate 4

**Model:** `sheneman/CerealPestAID`  
**Architecture:** EfficientNet-B6 / MobileNetV3-Large / InceptionV3  
**Task:** **Image classification** (no boxes)  
**Dataset:** `sheneman/CerealPestAID-dataset`  
**Classes (26 — from model card):**

Cabbage seedpod weevil; Bird cherry oat aphid; Cabbage aphid; Cereal grass aphid; Cereal leaf beetle; Clickbeetles / wireworms; Crucifer flea beetle; Cutworms; Diamondback moth; English grain aphid; Greenbug; Green peach aphid; Hessian fly; Lygus bug; Non-pest herbivores; Occasional pest; Pea aphid; Pea leaf weevil; Pea weevil; Predators; Rose grain aphid; Russian wheat aphid; Stink bug; Striped flea beetle; Turnip aphid; Wheathead armyworm

**Metrics (held-out test 2,381 images; not CropShield):**

| Variant | Test accuracy | Params | Weights |
|---------|---------------|--------|---------|
| EfficientNet-B6 | 92.94% | ~43M | ~469 MB `.pth` |
| MobileNetV3-Large | 90.09% | ~5.4M | ~49–51 MB |
| InceptionV3 | 79.00% | ~27M | ~289 MB |

**License:** MIT  
**Framework:** PyTorch / ONNX / TFLite  
**Preprocessing:** Resize 572 → center crop 528; ImageNet normalize  
**CPU:** MobileNet feasible; EfficientNet-B6 heavy  

**Real load:** **PASS** (MobileNetV3 with `state['model_state_dict']` — raw `load_state_dict(state)` fails)  
**Real inference:** **PASS_CLASSIFICATION_ONLY** on FAW train mosaic → predicted **Cereal grass aphid** conf **0.688966** in **209 ms** — **SMOKE / cross-domain only; not accuracy**. **No bounding boxes.**  
**Decision:** **REJECT for primary pest path** (fails desired OD contract). Keep as research reference for cereal classification only.

---

## Candidate 5

**Model:** `ViktorHarold/rice-pest-detector`  
**Architecture:** Claimed TensorFlow.js layers model  
**Task:** Binary classification (Healthy vs Pest-infected) — card only  
**Dataset:** Unspecified on card  
**Classes:** Not published as pest species list (binary only)  
**Metrics:** None published  
**License:** Unknown (not stated on card)  
**Repo contents:** Essentially README only — **no `model.json` / weights** (`RemoteEntryNotFoundError` for `tfjs_rice_pest_model/model.json`)  
**Real load:** **FAIL** — weights missing  
**Real inference:** **FAIL**  
**Decision:** **REJECT**

---

## Candidate 6 (additional)

**Model:** `Yudsky/pest-detection-yolo11`  
**Architecture:** YOLO11 OD  
**Dataset:** Kaggle IP102 YOLOv5 packaging (card)  
**Classes:** 102 names match IP102 list when loaded from weights  
**Metrics:** Card only shows epochs 1–5 (mAP50 up to **0.287**) — **incomplete / early training snapshot**  
**License:** Unclear on card  
**Real load:** **PASS** (102 classes)  
**Real inference:** **PASS**, 0 dets on FAW mosaic (~975 ms)  
**Decision:** **REJECT** vs underdogquality (same taxonomy, weaker/incomplete reported training)

**Also noted:** `Yashwanth1508/AgroAI-pest-detection` appears to be a **card clone** of underdogquality (same metrics/text) — not separately verified.

---

## Comparison Table

| Model | Task | Architecture | Pest Classes | Dataset | Metrics | Size | CPU | License | Deployment | Decision |
|-------|------|--------------|--------------|---------|---------|------|-----|---------|------------|----------|
| `underdogquality/yolo11s-pest-detection` | OD | YOLO11s | **102** (IP102 names) | IP102 | Val mAP@0.5 **0.815** (card) | ~38 MB | PASS ~4 s cold | MIT + IP102 academic caveat + Ultralytics AGPL dep | Best broad OD | **PRIMARY** |
| `Mustafa5645344/insect-detection-yolov8` | OD | YOLOv8m | **21** taxa | Specifly/Roboflow | Val mAP@50 **0.854** | ~47 MB | PASS ~0.7 s | Card MIT; `.pt` AGPL string | Coarser classes | **BACKUP** |
| `ndunge23/SambaGuard-v2` | OD | YOLOv8s | **4** FAW | KaraAgro maize (CC0) | Val mAP50 **0.347** | YOLOv8s | PASS ~0.4 s + **real boxes** | Apache-2.0 | Specialist only | **SPECIALIST** |
| `sheneman/CerealPestAID` | **Cls** | MobileNet/EffNet | **26** cereal | CerealPestAID-dataset | Acc up to **92.94%** | 49–469 MB | PASS cls | MIT | No boxes | **REJECT (OD)** |
| `ViktorHarold/rice-pest-detector` | Cls binary | TF.js (missing) | 2 (claimed) | Unknown | None | N/A | FAIL | Unknown | Incomplete repo | **REJECT** |
| `Yudsky/pest-detection-yolo11` | OD | YOLO11 | 102 | IP102 (Kaggle) | Incomplete (5 ep) | OD | PASS | Unclear | Weaker evidence | **REJECT** |

---

## Final Recommendation

### Primary pest model
**Exact model ID:** `underdogquality/yolo11s-pest-detection`  

**Why:**
- True **object detection** matching CropShield’s required outputs (class, box, confidence, count)
- **Widest verified class list** (102 exact IP102 names from `pests.yaml` + weights)
- Compact **~38 MB** weights; CPU inference verified
- MIT model card; most practical broad agricultural coverage among tested HF options

### Backup model
**Exact model ID:** `Mustafa5645344/insect-detection-yolov8`  

**Why:**
- Real OD with stronger **published validation mAP@50 (0.854)** and per-class tables
- Load/infer verified on CPU
- Useful if IP102 taxonomy or IP102 dataset licensing becomes blocking — Specifly/Roboflow lineage is different (but coarser 21 classes)

### Specialist (optional, not primary)
**Exact model ID:** `ndunge23/SambaGuard-v2` — only if product needs **Fall Armyworm** stage/damage detection on maize; Apache-2.0; **only model with confirmed non-zero box detections** in this research pass on a real repo sample image.

### Unsupported / Rejected
| Model | Why |
|-------|-----|
| `ViktorHarold/rice-pest-detector` | No downloadable weights; binary TF.js stub; unknown license |
| `sheneman/CerealPestAID` | Classification only — cannot supply bounding boxes / counts |
| `Yudsky/pest-detection-yolo11` | Incomplete training metrics; dominated by underdogquality |
| Card clones (e.g. AgroAI copy) | No independent evidence |

---

## Deployment estimate (vs current CropShield backend)

| Factor | Estimate / note |
|--------|-----------------|
| Extra dependency | `ultralytics` (+ its torch stack already present) — **AGPL-3.0** library license risk for SaaS |
| Weights download | ~38–47 MB primary/backup; SambaGuard similar small OD |
| RAM | Roughly **0.5–1.5 GB** additional peak for YOLO CPU predict (not profiled with tracemalloc; disease ViTs already dominate RAM) |
| Cold start | First predict ~1–5 s CPU observed; subsequent ~0.3–1 s |
| Inference time | YOLO11s ~4 s first / YOLO8m ~0.7 s / SambaGuard ~0.4 s on mosaics (CPU) |
| Render Docker | Feasible if `ultralytics` pinned; increases image size modestly vs another ViT |
| Disease stack conflict | **None if isolated** — do not alter disease HF registry; pest path should be separate |
| Legal | Review **IP102 academic dataset terms** + **Ultralytics AGPL** before production ship |

**Do not interpret smoke / cross-domain confidences as product accuracy.**

---

## Verification summary

| Model | Load | Inference | Boxes observed |
|-------|------|-----------|----------------|
| underdogquality/yolo11s-pest-detection | PASS | PASS | 0 on FAW mosaics (domain) |
| Mustafa5645344/insect-detection-yolov8 | PASS | PASS | 0 on FAW mosaics |
| ndunge23/SambaGuard-v2 | PASS | PASS | **2–6 real FAW boxes** on train mosaic |
| sheneman/CerealPestAID (MobileNet) | PASS | PASS (class only) | N/A |
| ViktorHarold/rice-pest-detector | FAIL | FAIL | N/A |
| Yudsky/pest-detection-yolo11 | PASS | PASS | 0 on FAW mosaics |

**No production pest code, disease code, frontend, RAG, or schema was modified.**
