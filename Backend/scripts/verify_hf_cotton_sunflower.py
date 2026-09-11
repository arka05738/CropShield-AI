"""
Isolated Cotton/Sunflower HF candidate verification.
Does NOT modify production registry. SMOKE TEST ONLY images.
"""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path

from PIL import Image, ImageDraw

BACKEND = Path(__file__).resolve().parents[1]
OUT = BACKEND.parent / "docs" / "_hf_cotton_sunflower_verify_raw.json"


def sample_jpeg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (224, 224), color=(34, 120, 40))
    d = ImageDraw.Draw(img)
    d.ellipse((40, 40, 180, 200), fill=(34, 120, 40))
    d.ellipse((70, 70, 110, 110), fill=(140, 70, 40))
    img.save(path, format="JPEG")
    return path


def verify_transformers(model_id: str, image_path: Path) -> dict:
    result = {
        "model_id": model_id,
        "framework": "transformers",
        "config_verified": False,
        "model_loaded": False,
        "real_inference": False,
        "status": "FAILED",
        "architecture": None,
        "num_labels": None,
        "id2label": {},
        "predicted_label": None,
        "confidence": None,
        "top3": [],
        "load_seconds": None,
        "infer_seconds": None,
        "params": None,
        "error": None,
        "note": "SMOKE TEST ONLY — synthetic leaf image",
    }
    try:
        import torch
        from transformers import AutoConfig, AutoImageProcessor, AutoModelForImageClassification

        t0 = time.time()
        cfg = AutoConfig.from_pretrained(model_id)
        id2label = {str(k): str(v) for k, v in dict(getattr(cfg, "id2label", {}) or {}).items()}
        result["architecture"] = (cfg.architectures or [cfg.model_type])[0]
        result["id2label"] = dict(sorted(id2label.items(), key=lambda x: int(x[0])))
        result["num_labels"] = len(id2label)
        result["config_verified"] = True

        processor = AutoImageProcessor.from_pretrained(model_id)
        model = AutoModelForImageClassification.from_pretrained(model_id)
        model.eval()
        result["model_loaded"] = True
        result["load_seconds"] = round(time.time() - t0, 3)
        result["params"] = sum(p.numel() for p in model.parameters())

        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        t1 = time.time()
        with torch.no_grad():
            logits = model(**inputs).logits[0]
            probs = torch.softmax(logits, dim=-1)
            topk = torch.topk(probs, k=min(3, probs.numel()))
        result["infer_seconds"] = round(time.time() - t1, 4)
        idx = int(topk.indices[0].item())
        result["predicted_label"] = id2label.get(str(idx), str(idx))
        result["confidence"] = round(float(topk.values[0].item()), 6)
        result["top3"] = [
            {"label": id2label.get(str(int(i)), str(int(i))), "confidence": round(float(v), 6)}
            for v, i in zip(topk.values.tolist(), topk.indices.tolist())
        ]
        result["real_inference"] = True
        result["status"] = "PASS"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()[-1500:]
        result["status"] = "FAILED"
    return result


def main() -> None:
    sample = sample_jpeg(BACKEND / "data" / "_hf_verify_samples" / "synthetic_leaf_cs.jpg")
    models = [
        "YaswanthReddy23/ViT_Cotton",
        "YaswanthReddy23/ViT_Sunflower",
        "ashishp-wiai/vit-base-patch16-224-in21k-finetuned-CottonPestClassification_v3a_os",
        "RohithN2004/Cotton-pests",
    ]
    out = {"note": "SMOKE TEST ONLY", "sample": str(sample), "models": {}}
    for mid in models:
        print(f"=== {mid} ===", flush=True)
        r = verify_transformers(mid, sample)
        out["models"][mid] = r
        print(
            f"status={r['status']} pred={r['predicted_label']} conf={r['confidence']} "
            f"load={r['load_seconds']} infer={r['infer_seconds']} err={r['error']}",
            flush=True,
        )
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT, flush=True)


if __name__ == "__main__":
    main()
