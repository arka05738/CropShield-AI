"""Dockerized backend: real HF HTTP diagnosis verification (no mock)."""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8005/api/v1"
OUT = Path(__file__).resolve().parents[2] / "docs" / "_docker_hf_results.json"

EXPECTED = {
    "Grape": "kimcomehome/plantvillage-vit-leaf-disease",
    "Sugarcane": "LishaV01/agriculture-crop-disease-detection",
    "Rice": "wambugu71/crop_leaf_diseases_vit",
    "Wheat": "wambugu71/crop_leaf_diseases_vit",
    "Cotton": "YaswanthReddy23/ViT_Cotton",
    "Sunflower": "YaswanthReddy23/ViT_Sunflower",
}


def leaf(seed: int = 0) -> bytes:
    img = Image.new("RGB", (224, 224), (20 + seed, 110, 35))
    d = ImageDraw.Draw(img)
    d.ellipse((30, 25, 200, 205), fill=(34, 140, 40), outline=(20, 80, 20))
    d.line((115, 35, 115, 195), fill=(80, 50, 20), width=4)
    for i in range(6):
        x, y = 55 + i * 18, 60 + (i * 13) % 100
        d.ellipse((x, y, x + 16, y + 12), fill=(130, 95, 35))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def main() -> int:
    report: dict = {"base": BASE, "health": None, "crops": {}, "millet": None, "authz": {}}
    h = requests.get(f"{BASE}/health", timeout=60)
    report["health"] = h.json()
    assert report["health"].get("disease_inference") == "HUGGINGFACE_MULTI_MODEL"
    assert report["health"].get("persistence_mode") == "mongodb"

    login = requests.post(
        f"{BASE}/auth/login",
        json={"email": "demo@cropshield.ai", "password": "cropshield123"},
        timeout=60,
    )
    login.raise_for_status()
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for crop, expected in EXPECTED.items():
        t0 = time.perf_counter()
        r = requests.post(
            f"{BASE}/diagnose",
            headers=headers,
            files={"file": ("leaf.jpg", leaf(hash(crop) % 30), "image/jpeg")},
            data={"crop_hint": crop, "latitude": "19.9975", "longitude": "73.7898"},
            timeout=900,
        )
        ms = round((time.perf_counter() - t0) * 1000, 1)
        body = r.json() if r.content else {}
        d = body.get("disease") or {}
        meta = body.get("inference_meta") or {}
        mid = meta.get("hf_disease_model_id") or d.get("model_name")
        report["crops"][crop] = {
            "http_status": r.status_code,
            "api_status": body.get("status"),
            "crop": body.get("crop"),
            "disease": d.get("disease"),
            "confidence": d.get("confidence"),
            "raw_label": meta.get("disease_raw_label") or d.get("raw_label"),
            "display_label": meta.get("disease_display_label") or d.get("display_label"),
            "model_id": mid,
            "expected_model": expected,
            "model_match": bool(mid and expected in str(mid)),
            "inference_mode": meta.get("disease_inference_mode") or d.get("inference_mode"),
            "rag_grounded": meta.get("rag_grounded"),
            "guidance_available": meta.get("guidance_available"),
            "analysis_id": body.get("id"),
            "total_ms": ms,
            "advisory_summary": ((body.get("advisory") or {}).get("condition_summary") or "")[:220],
        }
        print(crop, report["crops"][crop]["http_status"], mid, report["crops"][crop]["disease"], ms)

    # unsupported
    t0 = time.perf_counter()
    r = requests.post(
        f"{BASE}/diagnose",
        headers=headers,
        files={"file": ("leaf.jpg", leaf(1), "image/jpeg")},
        data={"crop_hint": "Millet", "latitude": "19.9975", "longitude": "73.7898"},
        timeout=120,
    )
    body = r.json()
    d = body.get("disease") or {}
    report["millet"] = {
        "http_status": r.status_code,
        "api_status": body.get("status"),
        "disease": d.get("disease"),
        "confidence": d.get("confidence"),
        "total_ms": round((time.perf_counter() - t0) * 1000, 1),
        "analysis_id": body.get("id"),
    }

    grape_id = report["crops"].get("Grape", {}).get("analysis_id")
    report["persist_id"] = grape_id
    hist = requests.get(f"{BASE}/analysis/history", headers=headers, timeout=60)
    report["history_before_restart"] = {
        "status": hist.status_code,
        "has_grape": any(isinstance(a, dict) and a.get("id") == grape_id for a in (hist.json() or [])),
    }

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"millet": report["millet"], "persist_id": grape_id}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
