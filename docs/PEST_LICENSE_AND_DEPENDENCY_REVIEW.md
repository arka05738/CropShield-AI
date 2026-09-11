# Pest License and Dependency Review

**Date:** 2026-09-11  
**Purpose:** Document licensing / dependency risks for the primary pest OD integration.  
**This is not legal advice.** Requires legal/license review before commercial deployment.

---

## 1. Model license

| Item | Value |
|------|-------|
| Model ID | `underdogquality/yolo11s-pest-detection` |
| Card / repo license | **MIT** |
| Weights file | `best.pt` (~38 MB) |
| Task | Object detection (102 IP102 classes) |

MIT permits use, modification, and distribution with copyright notice.  
**Requires legal/license review before commercial deployment** when combined with dataset and framework terms below.

---

## 2. Dataset terms (IP102)

| Item | Value |
|------|-------|
| Dataset | IP102 (CVPR 2019) |
| Upstream note | Authors state the dataset is free for **academic** usage; other purposes require contacting the authors |

CropShield did not redistribute the IP102 dataset files. The model was trained by a third party on IP102.  
Commercial products using IP102-derived models should obtain an independent legal review of dataset terms.

**Requires legal/license review before commercial deployment.**

---

## 3. Ultralytics dependency license

| Item | Value |
|------|-------|
| Package | `ultralytics` (added to `Backend/requirements.txt`) |
| Typical license | **AGPL-3.0** (Ultralytics open-source license) |
| Implication | Network use / SaaS may trigger AGPL source-disclosure obligations unless a commercial Ultralytics license is obtained |

CropShield’s disease path uses Hugging Face `transformers` + PyTorch and does **not** require Ultralytics.  
Pest OD currently depends on Ultralytics for YOLO predict.

**Requires legal/license review before commercial deployment.**

---

## 4. Suitability (non-legal engineering assessment)

| Use case | Engineering suitability | License note |
|----------|-------------------------|--------------|
| Academic demo / SIH showcase | **Suitable** with attribution | Still cite IP102 + model MIT + Ultralytics |
| Internal prototype / research | **Suitable** with documented AGPL awareness | Do not treat as production clearance |
| Commercial production SaaS | **Not cleared** | **Requires legal/license review before commercial deployment** (AGPL + IP102 terms) |

---

## 5. Implementation controls

- Model ID comes from config (`PEST_HF_MODEL_ID`) — no hardcoded credentials.
- HF token optional (`HF_TOKEN`) for Hub rate limits only.
- Backup and specialist models are **not** integrated in this step.
- Smoke-test / model-card metrics are **not** claimed as CropShield accuracy.

---

## 6. References

- Model card: https://huggingface.co/underdogquality/yolo11s-pest-detection  
- IP102 paper / GitHub dataset notice  
- Ultralytics license: https://ultralytics.com/license  
- Internal research: `docs/PEST_MODEL_RESEARCH.md`
