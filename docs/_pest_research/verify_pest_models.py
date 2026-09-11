"""Isolated pest-model research verification. Not part of CropShield production."""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path

from huggingface_hub import hf_hub_download
from PIL import Image, ImageDraw
from ultralytics import YOLO

OUT = Path(__file__).resolve().parent
RESULTS = OUT / "verification_results.json"


def make_smoke_image(path: Path) -> Path:
    """Synthetic leaf-ish image — SMOKE TEST ONLY."""
    img = Image.new("RGB", (640, 640), (34, 110, 40))
    d = ImageDraw.Draw(img)
    d.ellipse((220, 180, 420, 420), fill=(20, 80, 25), outline=(10, 50, 15))
    # small dark blobs that might trigger insect-like detections on some models
    for xy in [(260, 250, 290, 280), (340, 300, 375, 340), (300, 360, 330, 395)]:
        d.ellipse(xy, fill=(40, 25, 10))
    img.save(path, quality=92)
    return path


def download_real_sample(path: Path) -> tuple[Path, str]:
    """Prefer a real SambaGuard validation sample (FAW field imagery)."""
    try:
        p = hf_hub_download(
            repo_id="ndunge23/SambaGuard-v2",
            filename="validation_samples/val_batch0_labels.jpg",
            local_dir=str(OUT / "samples"),
        )
        return Path(p), "real_sample:ndunge23/SambaGuard-v2/validation_samples/val_batch0_labels.jpg"
    except Exception as e:
        smoke = make_smoke_image(path)
        return smoke, f"SMOKE TEST ONLY (real sample download failed: {e})"


def run_yolo(repo_id: str, filename: str, image: Path, conf: float = 0.25) -> dict:
    rec: dict = {
        "model_id": repo_id,
        "weights": filename,
        "load": "FAIL",
        "inference": "FAIL",
        "error": None,
        "class_names": None,
        "num_classes": None,
        "detections": [],
        "num_detections": 0,
        "load_s": None,
        "inference_ms": None,
        "weights_bytes": None,
    }
    try:
        t0 = time.perf_counter()
        weights = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=str(OUT / "weights" / repo_id.replace("/", "__")))
        rec["weights_bytes"] = Path(weights).stat().st_size
        model = YOLO(weights)
        rec["load_s"] = round(time.perf_counter() - t0, 3)
        names = model.names
        if isinstance(names, dict):
            rec["class_names"] = [names[i] for i in sorted(names)]
        else:
            rec["class_names"] = list(names)
        rec["num_classes"] = len(rec["class_names"])
        rec["load"] = "PASS"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-800:]}"
        return rec

    try:
        t1 = time.perf_counter()
        results = model.predict(source=str(image), imgsz=640, conf=conf, verbose=False, device="cpu")
        rec["inference_ms"] = round((time.perf_counter() - t1) * 1000, 1)
        dets = []
        r0 = results[0]
        if r0.boxes is not None and len(r0.boxes):
            for box in r0.boxes:
                cls_id = int(box.cls[0].item())
                conf_v = float(box.conf[0].item())
                xyxy = [round(float(x), 2) for x in box.xyxy[0].tolist()]
                dets.append(
                    {
                        "pest_class": rec["class_names"][cls_id] if rec["class_names"] else str(cls_id),
                        "class_id": cls_id,
                        "confidence": round(conf_v, 6),
                        "bbox_xyxy": xyxy,
                    }
                )
        rec["detections"] = dets
        rec["num_detections"] = len(dets)
        rec["inference"] = "PASS"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-800:]}"
    return rec


def main() -> None:
    smoke_path = OUT / "smoke_leaf.jpg"
    image, image_note = download_real_sample(smoke_path)
    # also keep a smoke image on disk for clarity
    make_smoke_image(smoke_path)

    candidates = [
        ("underdogquality/yolo11s-pest-detection", "best.pt"),
        ("Mustafa5645344/insect-detection-yolov8", "best.pt"),
        ("ndunge23/SambaGuard-v2", "weights/best.pt"),
    ]

    # Primary inference on real sample; secondary smoke only if zero detections (document both)
    report = {
        "image_used": str(image),
        "image_note": image_note,
        "smoke_image": str(smoke_path),
        "models": [],
    }

    for repo, fname in candidates:
        print(f"=== {repo} ===", flush=True)
        rec = run_yolo(repo, fname, image, conf=0.25)
        # If real sample yields 0 dets, also run smoke (explicitly labeled)
        if rec.get("inference") == "PASS" and rec.get("num_detections", 0) == 0:
            smoke_rec = run_yolo(repo, fname, smoke_path, conf=0.1)
            rec["smoke_followup"] = {
                "note": "SMOKE TEST ONLY — not accuracy evidence",
                "num_detections": smoke_rec.get("num_detections"),
                "detections": smoke_rec.get("detections"),
                "inference_ms": smoke_rec.get("inference_ms"),
                "inference": smoke_rec.get("inference"),
                "error": smoke_rec.get("error"),
            }
        report["models"].append(rec)
        print(json.dumps({k: rec[k] for k in ("model_id", "load", "inference", "num_classes", "num_detections", "inference_ms", "error")}, indent=2), flush=True)

    RESULTS.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("WROTE", RESULTS, flush=True)


if __name__ == "__main__":
    main()
