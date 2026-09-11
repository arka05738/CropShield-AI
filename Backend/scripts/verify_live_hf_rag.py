"""
Live HF → RAG verification via real HTTP POST /api/v1/diagnose.
Does NOT hardcode or substitute disease labels after inference.
"""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001/api/v1"
OUT = Path(__file__).resolve().parents[2] / "docs" / "_live_hf_rag_result.json"


def _leaf_jpeg() -> bytes:
    img = Image.new("RGB", (256, 256), color=(20, 90, 28))
    d = ImageDraw.Draw(img)
    d.ellipse((30, 20, 230, 240), fill=(34, 140, 40), outline=(15, 70, 20))
    d.line((128, 30, 128, 230), fill=(90, 55, 20), width=5)
    # lesion-like spots (not a labeled disease photo — model decides)
    for i, xy in enumerate([(70, 80), (150, 110), (100, 160), (170, 170), (90, 120)]):
        d.ellipse((xy[0], xy[1], xy[0] + 22, xy[1] + 16), fill=(140, 100, 40 + i * 5))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def main() -> int:
    health = requests.get(f"{BASE}/health", timeout=30).json()
    login = requests.post(
        f"{BASE}/auth/login",
        json={"email": "demo@cropshield.ai", "password": "cropshield123"},
        timeout=60,
    )
    login.raise_for_status()
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Explicit crop_hint — full production path; disease comes only from HF
    crop_hint = "Tomato"
    t0 = time.perf_counter()
    r = requests.post(
        f"{BASE}/diagnose",
        headers=headers,
        files={"file": ("tomato_leaf.jpg", _leaf_jpeg(), "image/jpeg")},
        data={
            "crop_hint": crop_hint,
            "latitude": "19.9975",
            "longitude": "73.7898",
            "language": "en",
        },
        timeout=600,
    )
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
    body = r.json()
    disease = body.get("disease") or {}
    meta = body.get("inference_meta") or {}
    advisory = body.get("advisory") or {}
    pesticide = advisory.get("pesticide_recommendation") or {}

    disease_name = disease.get("disease") or disease.get("display_label")
    guidance = bool(pesticide.get("guidance_available"))
    sources = advisory.get("sources") or []
    rag_grounded = bool(meta.get("rag_grounded")) or bool(sources)
    is_healthy = (disease.get("pathogen_type") or "").lower() == "healthy" or (
        isinstance(disease_name, str) and "healthy" in disease_name.lower()
    )
    dose = (pesticide.get("exact_dose_per_liter") or "").strip()
    chemical = pesticide.get("chemical_name") or ""

    if body.get("status") == "model_unavailable":
        outcome = "LIVE HF → RAG N/A (model_unavailable)"
        rag_class = "n/a"
    elif is_healthy and guidance and not rag_grounded:
        outcome = "LIVE HF → HEALTHY PATH (not disease RAG)"
        rag_class = "healthy_path"
    elif guidance and (rag_grounded or dose):
        outcome = "LIVE HF → RAG HIT"
        rag_class = "hit"
    else:
        outcome = "LIVE HF → RAG MISS"
        rag_class = "miss"

    # Safety: on miss / unavailable, no invented dosage
    invented = False
    if rag_class in ("miss", "n/a"):
        invented = bool(dose) or (
            chemical
            and "unavailable" not in chemical.lower()
            and chemical.lower() not in ("not specified", "")
        )

    result = {
        "outcome": outcome,
        "rag_class": rag_class,
        "http_status": r.status_code,
        "api_status": body.get("status"),
        "elapsed_ms": elapsed_ms,
        "health_disease_inference": health.get("disease_inference"),
        "health_persistence_mode": health.get("persistence_mode"),
        "crop_hint": crop_hint,
        "crop": body.get("crop"),
        "raw_label": meta.get("disease_raw_label") or disease.get("raw_label"),
        "display_label": meta.get("disease_display_label") or disease.get("display_label"),
        "disease": disease_name,
        "confidence": disease.get("confidence"),
        "inference_mode": meta.get("disease_inference_mode") or disease.get("inference_mode"),
        "model_id": meta.get("hf_disease_model_id") or disease.get("model_name"),
        "model_provider": disease.get("model_provider"),
        "model_architecture": meta.get("hf_model_architecture") or disease.get("model_architecture"),
        "rag_query_key": {
            "crop": body.get("crop"),
            "disease": disease_name,
        },
        "rag_grounded": rag_grounded,
        "guidance_available": guidance,
        "sources_count": len(sources),
        "sources": sources,
        "pesticide": pesticide,
        "condition_summary": (advisory.get("condition_summary") or "")[:400],
        "invented_dosage_on_miss": invented,
        "analysis_id": body.get("id"),
        "normalization_note": (
            "AdvisoryEngine._match_record uses case-insensitive crop equality and "
            "substring disease match (KB disease in predicted name or vice versa). "
            "No post-inference label rewriting in the diagnose path."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if r.status_code == 200 and not invented else 1


if __name__ == "__main__":
    raise SystemExit(main())
