"""
Isolated Hugging Face candidate verification — NOT part of production API.
Does not use USE_MOCK_AI, heuristics, or mocked logits.
Run: python scripts/verify_hf_candidates.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

from PIL import Image, ImageDraw

BACKEND = Path(__file__).resolve().parents[1]
OUT = BACKEND.parent / "docs" / "_hf_candidate_verify_raw.json"
sys.path.insert(0, str(BACKEND))


def make_sample(path: Path, color=(34, 120, 40), blotch=(120, 80, 30)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (224, 224), color=color)
    d = ImageDraw.Draw(img)
    d.ellipse((40, 40, 180, 200), fill=color)
    d.ellipse((70, 70, 110, 110), fill=blotch)
    d.ellipse((120, 130, 160, 165), fill=(90, 60, 20))
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
        "error": None,
        "load_seconds": None,
        "infer_seconds": None,
        "param_estimate": None,
    }
    try:
        from transformers import AutoConfig, AutoImageProcessor, AutoModelForImageClassification
        import torch

        t0 = time.time()
        cfg = AutoConfig.from_pretrained(model_id)
        result["architecture"] = (cfg.architectures or [cfg.model_type])[0]
        id2label = {str(k): str(v) for k, v in dict(getattr(cfg, "id2label", {}) or {}).items()}
        result["id2label"] = dict(sorted(id2label.items(), key=lambda x: int(x[0])))
        result["num_labels"] = len(id2label)
        result["config_verified"] = True

        processor = AutoImageProcessor.from_pretrained(model_id)
        model = AutoModelForImageClassification.from_pretrained(model_id)
        model.eval()
        result["model_loaded"] = True
        result["load_seconds"] = round(time.time() - t0, 2)
        result["param_estimate"] = sum(p.numel() for p in model.parameters())

        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        t1 = time.time()
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0]
            probs = torch.softmax(logits, dim=-1)
            topk = torch.topk(probs, k=min(3, probs.numel()))
        result["infer_seconds"] = round(time.time() - t1, 3)
        idx = int(topk.indices[0].item())
        label = id2label.get(str(idx), str(idx))
        conf = float(topk.values[0].item())
        result["predicted_label"] = label
        result["confidence"] = round(conf, 6)
        result["top3"] = [
            {
                "label": id2label.get(str(int(i)), str(int(i))),
                "confidence": round(float(v), 6),
            }
            for v, i in zip(topk.values.tolist(), topk.indices.tolist())
        ]
        result["real_inference"] = True
        result["status"] = "PASS"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()[-2000:]
        result["status"] = "FAILED"
    return result


def verify_arko(model_id: str, image_path: Path) -> dict:
    """Arko007/nfnet-f1-plant-disease — timm + safetensors, not transformers AutoModel."""
    result = {
        "model_id": model_id,
        "framework": "timm+safetensors",
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
        "error": None,
        "load_seconds": None,
        "infer_seconds": None,
        "param_estimate": None,
        "license_note": "cc-by-nc-sa-4.0 (non-commercial per Hub card)",
    }
    try:
        from huggingface_hub import hf_hub_download
        import torch
        import timm
        from safetensors.torch import load_file
        from torchvision import transforms

        t0 = time.time()
        cfg_path = hf_hub_download(model_id, "config.json")
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        class_names = list(cfg.get("class_names") or [])
        result["architecture"] = cfg.get("architecture")
        result["num_labels"] = len(class_names)
        result["id2label"] = {str(i): n for i, n in enumerate(class_names)}
        result["config_verified"] = True
        input_size = int(cfg.get("input_size") or 512)
        mean = cfg.get("normalization", {}).get("mean", [0.5, 0.5, 0.5])
        std = cfg.get("normalization", {}).get("std", [0.5, 0.5, 0.5])

        weights = hf_hub_download(model_id, "model.safetensors")
        model = timm.create_model(
            cfg["architecture"], pretrained=False, num_classes=len(class_names)
        )
        state = load_file(weights)
        model.load_state_dict(state)
        model.eval()
        result["model_loaded"] = True
        result["load_seconds"] = round(time.time() - t0, 2)
        result["param_estimate"] = sum(p.numel() for p in model.parameters())

        tfm = transforms.Compose(
            [
                transforms.Resize((input_size, input_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=mean, std=std),
            ]
        )
        image = Image.open(image_path).convert("RGB")
        batch = tfm(image).unsqueeze(0)
        t1 = time.time()
        with torch.no_grad():
            logits = model(batch)[0]
            probs = torch.softmax(logits, dim=-1)
            topk = torch.topk(probs, k=min(3, probs.numel()))
        result["infer_seconds"] = round(time.time() - t1, 3)
        idx = int(topk.indices[0].item())
        result["predicted_label"] = class_names[idx]
        result["confidence"] = round(float(topk.values[0].item()), 6)
        result["top3"] = [
            {
                "label": class_names[int(i)],
                "confidence": round(float(v), 6),
            }
            for v, i in zip(topk.values.tolist(), topk.indices.tolist())
        ]
        result["real_inference"] = True
        result["status"] = "PASS"
        # metrics if present
        try:
            mpath = hf_hub_download(model_id, "metrics.json")
            with open(mpath, encoding="utf-8") as f:
                result["card_metrics_file"] = json.load(f)
        except Exception:
            result["card_metrics_file"] = None
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()[-2000:]
        result["status"] = "FAILED"
    return result


def crop_support_from_labels(id2label: dict, crop_keywords: list[str]) -> list[str]:
    hits = []
    for lab in id2label.values():
        low = lab.lower().replace("_", " ")
        if any(k in low for k in crop_keywords):
            hits.append(lab)
    return sorted(set(hits))


def main() -> None:
    sample_dir = BACKEND / "data" / "_hf_verify_samples"
    sample = make_sample(sample_dir / "synthetic_leaf.jpg")

    results = {
        "note": (
            "Synthetic leaf image used for load/inference smoke only. "
            "Does NOT validate disease diagnostic accuracy."
        ),
        "sample_image": str(sample),
        "models": {},
    }

    # Current + transformers candidates
    for mid in [
        "kimcomehome/plantvillage-vit-leaf-disease",
        "wambugu71/crop_leaf_diseases_vit",
        "LishaV01/agriculture-crop-disease-detection",
    ]:
        print(f"\n=== Verifying {mid} ===", flush=True)
        results["models"][mid] = verify_transformers(mid, sample)
        r = results["models"][mid]
        print(
            f"config={r['config_verified']} loaded={r['model_loaded']} "
            f"infer={r['real_inference']} status={r['status']} "
            f"pred={r['predicted_label']} conf={r['confidence']} err={r['error']}",
            flush=True,
        )

    print("\n=== Verifying Arko007/nfnet-f1-plant-disease ===", flush=True)
    results["models"]["Arko007/nfnet-f1-plant-disease"] = verify_arko(
        "Arko007/nfnet-f1-plant-disease", sample
    )
    r = results["models"]["Arko007/nfnet-f1-plant-disease"]
    print(
        f"config={r['config_verified']} loaded={r['model_loaded']} "
        f"infer={r['real_inference']} status={r['status']} "
        f"pred={r['predicted_label']} conf={r['confidence']} err={r['error']}",
        flush=True,
    )

    # Crop support matrix from verified labels only
    matrix = {}
    for mid, r in results["models"].items():
        labels = r.get("id2label") or {}
        matrix[mid] = {
            "Sugarcane": crop_support_from_labels(labels, ["sugarcane"]),
            "Rice": crop_support_from_labels(labels, ["rice"]),
            "Wheat": crop_support_from_labels(labels, ["wheat"]),
            "Grape": crop_support_from_labels(labels, ["grape"]),
            "Cotton": crop_support_from_labels(labels, ["cotton"]),
            "Sunflower": crop_support_from_labels(labels, ["sunflower"]),
            "Tomato": crop_support_from_labels(labels, ["tomato"]),
            "Potato": crop_support_from_labels(labels, ["potato"]),
            "Maize/Corn": crop_support_from_labels(labels, ["corn", "maize"]),
        }
    results["crop_label_hits"] = matrix

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
