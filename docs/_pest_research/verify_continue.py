"""Continue pest verification for remaining models."""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path

from huggingface_hub import hf_hub_download
from ultralytics import YOLO

OUT = Path(r"C:\Users\ARKA\Downloads\crop_Project_SIH\docs\_pest_research")
img = OUT / "samples" / "validation_samples" / "val_batch0_labels.jpg"
smoke = OUT / "smoke_leaf.jpg"


def run(repo: str, filename: str, image: Path, conf: float = 0.25) -> dict:
    rec: dict = {
        "model_id": repo,
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
        "image": str(image),
    }
    try:
        t0 = time.perf_counter()
        wdir = OUT / "weights" / repo.replace("/", "__")
        weights = hf_hub_download(repo_id=repo, filename=filename, local_dir=str(wdir))
        rec["weights_bytes"] = Path(weights).stat().st_size
        model = YOLO(weights)
        rec["load_s"] = round(time.perf_counter() - t0, 3)
        names = model.names
        rec["class_names"] = [names[i] for i in sorted(names)] if isinstance(names, dict) else list(names)
        rec["num_classes"] = len(rec["class_names"])
        rec["load"] = "PASS"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1200:]}"
        return rec
    try:
        t1 = time.perf_counter()
        results = model.predict(source=str(image), imgsz=640, conf=conf, verbose=False, device="cpu")
        rec["inference_ms"] = round((time.perf_counter() - t1) * 1000, 1)
        dets = []
        r0 = results[0]
        if r0.boxes is not None:
            for box in r0.boxes:
                cid = int(box.cls[0].item())
                dets.append(
                    {
                        "pest_class": rec["class_names"][cid],
                        "class_id": cid,
                        "confidence": round(float(box.conf[0].item()), 6),
                        "bbox_xyxy": [round(float(x), 2) for x in box.xyxy[0].tolist()],
                    }
                )
        rec["detections"] = dets[:20]
        rec["num_detections"] = len(dets)
        rec["inference"] = "PASS"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1200:]}"
    return rec


def main() -> None:
    print("=== underdogquality ===", flush=True)
    under = run("underdogquality/yolo11s-pest-detection", "best.pt", img, 0.25)
    print("under", under["load"], under["inference"], under["num_detections"], under["inference_ms"], flush=True)

    print("=== Mustafa ===", flush=True)
    must = run("Mustafa5645344/insect-detection-yolov8", "best.pt", img, 0.25)
    print("must", must["load"], must["inference"], must["num_detections"], must["inference_ms"], must.get("error"), flush=True)

    print("=== SambaGuard ===", flush=True)
    samba = run("ndunge23/SambaGuard-v2", "weights/best.pt", img, 0.25)
    print(
        "samba",
        samba["load"],
        samba["inference"],
        samba["num_detections"],
        samba["inference_ms"],
        samba.get("class_names"),
        flush=True,
    )
    if samba.get("detections"):
        print("samba_first", samba["detections"][:5], flush=True)

    for rec in (under, must):
        if rec.get("num_detections", 0) == 0 and rec.get("load") == "PASS":
            s = run(rec["model_id"], rec["weights"], smoke, 0.05)
            rec["smoke_followup"] = {
                "note": "SMOKE TEST ONLY — not accuracy evidence",
                "num_detections": s.get("num_detections"),
                "detections": s.get("detections"),
                "inference_ms": s.get("inference_ms"),
                "inference": s.get("inference"),
                "error": s.get("error"),
            }

    cereal = {
        "model_id": "sheneman/CerealPestAID",
        "task": "image-classification",
        "load": "FAIL",
        "inference": "SKIP_NOT_DETECTION",
    }
    try:
        t0 = time.perf_counter()
        pth = hf_hub_download(
            repo_id="sheneman/CerealPestAID",
            filename="mobilenetv3/best_factai_mobilenetv3.pth",
            local_dir=str(OUT / "weights" / "CerealPestAID"),
        )
        import torch
        import torch.nn as nn
        from PIL import Image
        from torchvision import models, transforms

        model = models.mobilenet_v3_large(weights=None)
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, 26)
        state = torch.load(pth, map_location="cpu")
        model.load_state_dict(state)
        model.eval()
        cereal["load"] = "PASS"
        cereal["load_s"] = round(time.perf_counter() - t0, 3)
        cereal["weights_bytes"] = Path(pth).stat().st_size
        cereal["note"] = "Classification only — no bounding boxes"
        tfm = transforms.Compose(
            [
                transforms.Resize(572),
                transforms.CenterCrop(528),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
        x = tfm(Image.open(img).convert("RGB")).unsqueeze(0)
        t1 = time.perf_counter()
        with torch.no_grad():
            out = model(x)
            pred = int(torch.argmax(out, dim=1).item())
            conf = float(torch.softmax(out, dim=1)[0, pred].item())
        cereal["inference"] = "PASS_CLASSIFICATION_ONLY"
        cereal["pred_class_index"] = pred
        cereal["confidence"] = round(conf, 6)
        cereal["inference_ms"] = round((time.perf_counter() - t1) * 1000, 1)
        print("cereal", cereal["load"], cereal["inference"], cereal["pred_class_index"], cereal["confidence"], flush=True)
    except Exception as e:
        cereal["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1200:]}"
        print("cereal FAIL", cereal["error"][:500], flush=True)

    vik = {"model_id": "ViktorHarold/rice-pest-detector", "load": "FAIL", "inference": "FAIL"}
    try:
        hf_hub_download(
            repo_id="ViktorHarold/rice-pest-detector",
            filename="tfjs_rice_pest_model/model.json",
        )
        vik["load"] = "UNEXPECTED_FILE_FOUND"
    except Exception as e:
        vik["error"] = f"{type(e).__name__}: {e}"
        print("viktor", vik["error"][:300], flush=True)

    # Yudsky incomplete training — inspect only if quick
    yud = {"model_id": "Yudsky/pest-detection-yolo11", "note": "researched; metrics incomplete (5 epochs only)"}
    try:
        y = run("Yudsky/pest-detection-yolo11", "best.pt", img, 0.25)
        yud.update(y)
        print("yudsky", yud.get("load"), yud.get("num_detections"), yud.get("error"), flush=True)
    except Exception as e:
        yud["error"] = str(e)

    report = {
        "image_used": str(img),
        "image_note": "real_sample: SambaGuard validation collage (FAW labels visualization)",
        "models": [under, must, samba, cereal, vik, yud],
    }
    out_path = OUT / "verification_results.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("WROTE", out_path, flush=True)


if __name__ == "__main__":
    main()
