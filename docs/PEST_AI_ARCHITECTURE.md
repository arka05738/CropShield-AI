# Pest AI Architecture

**Date:** 2026-09-11  
**Primary model:** `underdogquality/yolo11s-pest-detection`  
**Scope:** Dedicated pest object-detection path (disease `/diagnose` unchanged)

---

## Pipeline

```
image
 ↓
upload validation (size / ext / MIME / magic / PIL / path safety)
 ↓
POST /api/v1/pests/detect  (JWT farmer auth)
 ↓
pest detector (lazy Ultralytics YOLO11s, cached)
 ↓
bounding boxes (x1,y1,x2,y2 pixel) + exact raw_label
 ↓
confidence filter (PEST_CONFIDENCE_THRESHOLD, default 0.25)
 ↓
count
 ↓
preliminary severity (low|moderate|high|none) — labeled as AI estimate
 ↓
RAG pest advisory (curated match only; else guidance_available=false)
 ↓
history → pest_analyses (Mongo + memory; separate from disease analyses)
```

---

## Configuration

| Env | Default | Meaning |
|-----|---------|---------|
| `USE_PEST_HF_MODEL` | `true` | Enable primary HF pest OD |
| `PEST_HF_MODEL_ID` | `underdogquality/yolo11s-pest-detection` | Exact model ID |
| `PEST_CONFIDENCE_THRESHOLD` | `0.25` | Ultralytics-style detection filter — **not accuracy** |
| `PEST_MODEL_PATH` | empty | Optional local `.pt` override |
| `USE_MOCK_PEST` | `false` | Diagnose-path mock only; OD endpoint refuses mock fabrication |

Author-reported model-card validation **mAP@0.5 = 0.815** / **mAP@0.5:0.95 = 0.605** are **not** CropShield accuracy.

---

## API

- `POST /api/v1/pests/detect` — multipart `file` + optional `crop_hint`
- `GET /api/v1/pests/history` — farmer-owned pest OD history
- `GET /api/v1/pests/{id}` — single pest record
- Admin: `GET /api/v1/admin/pests` — pest cases distinct from diseases

Status values:
- `pests_detected` when `count > 0`
- `no_pest_detected` when model returns zero boxes (does **not** mean “no pests exist”)

---

## Module layout

```
Backend/app/ml/pest/
  pest_registry.py
  pest_model_loader.py
  pest_detector.py
  pest_schema.py
  preprocessing.py
```

Backup / specialist models are **registered in docs only** — not loaded:
- Backup: `Mustafa5645344/insect-detection-yolov8`
- Specialist: `ndunge23/SambaGuard-v2`

---

## Limitations

- Zero detections on non-insect / collage / out-of-domain images is expected and valid.
- Preliminary severity is a transparent heuristic (count / confidence / box density), **not** agronomic % damage.
- RAG chemicals only when curated pest label match exists.
- Ultralytics AGPL + IP102 dataset terms require legal review before commercial production (see `PEST_LICENSE_AND_DEPENDENCY_REVIEW.md`).
- Disease and pest histories are separate; diagnose still uses the legacy empty/mock pest stub and does not write `pest_analyses`.
