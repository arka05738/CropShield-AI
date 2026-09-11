"""
End-to-end HTTP diagnosis verification against a running CropShield API.

Requires: uvicorn already listening (default http://127.0.0.1:8000).
Does NOT enable USE_MOCK_AI. Uses real multipart uploads + authenticated farmer.

Usage:
  python scripts/e2e_diagnosis_verification.py [--base-url URL] [--out PATH]
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from PIL import Image, ImageDraw

EXPECTED_MODELS = {
    "Grape": "kimcomehome/plantvillage-vit-leaf-disease",
    "Sugarcane": "LishaV01/agriculture-crop-disease-detection",
    "Rice": "wambugu71/crop_leaf_diseases_vit",
    "Wheat": "wambugu71/crop_leaf_diseases_vit",
    "Cotton": "YaswanthReddy23/ViT_Cotton",
    "Sunflower": "YaswanthReddy23/ViT_Sunflower",
}


def _leaf_jpeg(seed: int = 0) -> bytes:
    img = Image.new("RGB", (224, 224), color=(28 + seed, 120, 40))
    draw = ImageDraw.Draw(img)
    draw.ellipse((40, 30, 190, 200), fill=(34, 139, 34), outline=(20, 80, 20))
    draw.line((110, 40, 110, 190), fill=(80, 50, 20), width=4)
    for i in range(8):
        x = 60 + (i * 15 + seed) % 100
        y = 50 + (i * 17) % 120
        draw.ellipse((x, y, x + 18, y + 12), fill=(120, 90, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def _safe_json(r: requests.Response) -> Any:
    if not r.content:
        return {}
    try:
        return r.json()
    except Exception:
        return {"_non_json": True, "_text": (r.text or "")[:300], "_content_type": r.headers.get("content-type")}


def _login(base: str, email: str, password: str = "cropshield123") -> Dict[str, Any]:
    r = requests.post(
        f"{base}/auth/login",
        json={"email": email, "password": password},
        timeout=60,
    )
    return {"status_code": r.status_code, "body": _safe_json(r)}


def _auth(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _diagnose(
    base: str,
    token: str,
    crop_hint: Optional[str],
    image_bytes: bytes,
    filename: str = "leaf.jpg",
    content_type: str = "image/jpeg",
    extra_data: Optional[Dict[str, Any]] = None,
    timeout: int = 600,
) -> Dict[str, Any]:
    data: Dict[str, Any] = {"latitude": "19.9975", "longitude": "73.7898"}
    if crop_hint is not None:
        data["crop_hint"] = crop_hint
    if extra_data:
        data.update(extra_data)
    t0 = time.perf_counter()
    r = requests.post(
        f"{base}/diagnose",
        headers=_auth(token),
        files={"file": (filename, image_bytes, content_type)},
        data=data,
        timeout=timeout,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000
    try:
        body = _safe_json(r)
    except Exception:
        body = {"raw": r.text[:500]}
    return {"status_code": r.status_code, "elapsed_ms": round(elapsed_ms, 1), "body": body}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[2] / "docs" / "_e2e_results.json"),
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    report: Dict[str, Any] = {"base_url": base, "tests": {}}

    # Health
    t0 = time.perf_counter()
    h = requests.get(f"{base}/health", timeout=30)
    report["tests"]["health"] = {
        "status_code": h.status_code,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
        "body": h.json() if h.content else {},
    }

    # Auth farmer
    login = _login(base, "demo@cropshield.ai")
    report["tests"]["auth_farmer"] = {
        "status_code": login["status_code"],
        "role": (login["body"].get("user") or {}).get("role"),
        "has_token": "access_token" in login["body"],
    }
    if login["status_code"] != 200:
        Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 1
    farmer_token = login["body"]["access_token"]
    farmer_id = login["body"]["user"]["id"]

    # Admin auth
    admin_login = _login(base, "admin@cropshield.ai")
    report["tests"]["auth_admin"] = {
        "status_code": admin_login["status_code"],
        "role": (admin_login["body"].get("user") or {}).get("role"),
    }
    admin_token = admin_login["body"].get("access_token")

    # Crop routing + real inference
    crop_results: Dict[str, Any] = {}
    for crop, expected_model in EXPECTED_MODELS.items():
        res = _diagnose(base, farmer_token, crop, _leaf_jpeg(hash(crop) % 40))
        body = res["body"]
        disease = body.get("disease") or {}
        meta = body.get("inference_meta") or {}
        model_id = meta.get("hf_disease_model_id") or meta.get("disease_model_name")
        crop_results[crop] = {
            "http_status": res["status_code"],
            "api_status": body.get("status"),
            "crop": body.get("crop"),
            "disease": disease.get("disease") if isinstance(disease, dict) else disease,
            "confidence": disease.get("confidence") if isinstance(disease, dict) else None,
            "inference_mode": meta.get("disease_inference_mode")
            or (disease.get("inference_mode") if isinstance(disease, dict) else None),
            "model_id": model_id,
            "expected_model": expected_model,
            "model_match": bool(model_id and expected_model in str(model_id)),
            "raw_label": meta.get("disease_raw_label")
            or (disease.get("raw_label") if isinstance(disease, dict) else None),
            "display_label": meta.get("disease_display_label")
            or (disease.get("display_label") if isinstance(disease, dict) else None),
            "architecture": meta.get("hf_model_architecture")
            or (disease.get("model_architecture") if isinstance(disease, dict) else None),
            "provider": (disease.get("model_provider") if isinstance(disease, dict) else None),
            "rag_grounded": meta.get("rag_grounded"),
            "guidance_available": meta.get("guidance_available"),
            "analysis_id": body.get("id"),
            "total_api_ms": res["elapsed_ms"],
            "advisory_summary": ((body.get("advisory") or {}).get("condition_summary") or "")[:200],
        }
    report["tests"]["crops"] = crop_results
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    # Unsupported crop
    unsup = _diagnose(base, farmer_token, "Millet", _leaf_jpeg(7))
    ub = unsup["body"]
    ud = ub.get("disease") or {}
    report["tests"]["unsupported_millet"] = {
        "http_status": unsup["status_code"],
        "api_status": ub.get("status"),
        "disease": ud.get("disease") if isinstance(ud, dict) else ud,
        "confidence": ud.get("confidence") if isinstance(ud, dict) else None,
        "inference_mode": (ub.get("inference_meta") or {}).get("disease_inference_mode"),
        "total_api_ms": unsup["elapsed_ms"],
    }

    # Invalid inputs
    invalid: Dict[str, Any] = {}
    # invalid file type
    r = requests.post(
        f"{base}/diagnose",
        headers=_auth(farmer_token),
        files={"file": ("notes.txt", b"not an image", "text/plain")},
        data={"crop_hint": "Grape"},
        timeout=60,
    )
    invalid["invalid_file_type"] = {"status_code": r.status_code, "detail": _safe_json(r)}

    # oversized (create ~11MB)
    big = b"\xff\xd8\xff" + (b"0" * (11 * 1024 * 1024))
    r = requests.post(
        f"{base}/diagnose",
        headers=_auth(farmer_token),
        files={"file": ("big.jpg", big, "image/jpeg")},
        data={"crop_hint": "Grape"},
        timeout=60,
    )
    invalid["oversized"] = {"status_code": r.status_code, "detail": _safe_json(r)}

    # corrupted
    r = requests.post(
        f"{base}/diagnose",
        headers=_auth(farmer_token),
        files={"file": ("bad.jpg", b"\xff\xd8\xff\x00notjpeg", "image/jpeg")},
        data={"crop_hint": "Grape"},
        timeout=60,
    )
    invalid["corrupted"] = {"status_code": r.status_code, "detail": _safe_json(r)}

    # empty
    r = requests.post(
        f"{base}/diagnose",
        headers=_auth(farmer_token),
        files={"file": ("empty.jpg", b"", "image/jpeg")},
        data={"crop_hint": "Grape"},
        timeout=60,
    )
    invalid["empty"] = {"status_code": r.status_code, "detail": _safe_json(r)}

    # no auth
    r = requests.post(
        f"{base}/diagnose",
        files={"file": ("leaf.jpg", _leaf_jpeg(), "image/jpeg")},
        data={"crop_hint": "Grape"},
        timeout=60,
    )
    invalid["missing_auth"] = {"status_code": r.status_code}

    # bad token
    r = requests.post(
        f"{base}/diagnose",
        headers={"Authorization": "Bearer not-a-real-token"},
        files={"file": ("leaf.jpg", _leaf_jpeg(), "image/jpeg")},
        data={"crop_hint": "Grape"},
        timeout=60,
    )
    invalid["invalid_auth"] = {"status_code": r.status_code}

    # farmer vs admin
    r = requests.get(f"{base}/admin/stats", headers=_auth(farmer_token), timeout=30)
    invalid["farmer_admin_forbidden"] = {"status_code": r.status_code}
    if admin_token:
        r = requests.get(f"{base}/admin/stats", headers=_auth(admin_token), timeout=30)
        body = _safe_json(r)
        invalid["admin_stats_ok"] = {
            "status_code": r.status_code,
            "keys": list(body.keys())[:12] if isinstance(body, dict) else [],
        }
        r = requests.get(f"{base}/admin/cases", headers=_auth(admin_token), timeout=30)
        cases = _safe_json(r)
        case_count = None
        if isinstance(cases, dict):
            case_count = cases.get("count")
            if case_count is None and isinstance(cases.get("cases"), list):
                case_count = len(cases["cases"])
        elif isinstance(cases, list):
            case_count = len(cases)
        # sample model metadata if present
        sample_model = None
        if isinstance(cases, dict):
            for c in cases.get("cases") or []:
                if isinstance(c, dict) and c.get("model"):
                    sample_model = c.get("model")
                    break
        invalid["admin_cases"] = {
            "status_code": r.status_code,
            "count": case_count,
            "sample_model": sample_model,
        }
        r = requests.get(f"{base}/admin/models", headers=_auth(admin_token), timeout=30)
        invalid["admin_models"] = {
            "status_code": r.status_code,
            "body_preview": str(_safe_json(r))[:400],
        }
    report["tests"]["invalid_and_authz"] = invalid

    # History + isolation
    hist = requests.get(f"{base}/analysis/history", headers=_auth(farmer_token), timeout=60)
    hist_body = _safe_json(hist)
    if not isinstance(hist_body, list):
        hist_body = []
    grape_id = crop_results.get("Grape", {}).get("analysis_id")
    grape_rec = next((a for a in hist_body if isinstance(a, dict) and a.get("id") == grape_id), None)
    report["tests"]["history_farmer"] = {
        "status_code": hist.status_code,
        "count": len(hist_body) if isinstance(hist_body, list) else None,
        "grape_record_found": grape_rec is not None,
        "grape_fields": {
            "crop": grape_rec.get("crop") if grape_rec else None,
            "disease": (grape_rec.get("disease") or {}).get("disease") if grape_rec else None,
            "confidence": (grape_rec.get("disease") or {}).get("confidence") if grape_rec else None,
            "raw_label": (grape_rec.get("inference_meta") or {}).get("disease_raw_label") if grape_rec else None,
            "display_label": (grape_rec.get("inference_meta") or {}).get("disease_display_label") if grape_rec else None,
            "model": grape_rec.get("model") if grape_rec else None,
            "created_at": grape_rec.get("created_at") if grape_rec else None,
            "user_id": grape_rec.get("user_id") if grape_rec else None,
            "user_matches": (grape_rec.get("user_id") == farmer_id) if grape_rec else None,
        },
    }

    # Register second farmer and try to access first farmer's analysis
    email2 = f"e2e_farmer_{int(time.time())}@cropshield.ai"
    reg = requests.post(
        f"{base}/auth/register",
        json={
            "email": email2,
            "password": "cropshield123",
            "full_name": "E2E Farmer Two",
            "role": "FARMER",
        },
        timeout=60,
    )
    isolation: Dict[str, Any] = {"register_status": reg.status_code, "email": email2}
    if reg.status_code in (200, 201):
        token2 = (_safe_json(reg) or {}).get("access_token")
        if grape_id and token2:
            r = requests.get(f"{base}/analysis/{grape_id}", headers=_auth(token2), timeout=30)
            isolation["cross_farmer_get"] = {"status_code": r.status_code, "detail": _safe_json(r)}
            r = requests.get(f"{base}/analysis/history", headers=_auth(token2), timeout=30)
            other_hist = _safe_json(r)
            isolation["second_farmer_history_count"] = len(other_hist) if isinstance(other_hist, list) else None
            isolation["second_sees_grape"] = any(
                isinstance(a, dict) and a.get("id") == grape_id for a in (other_hist or [])
            )
    report["tests"]["history_isolation"] = isolation

    # RAG spot-check: Tomato often has KB; exotic disease label may not
    tomato = _diagnose(base, farmer_token, "Tomato", _leaf_jpeg(3))
    tb = tomato["body"]
    report["tests"]["rag_tomato"] = {
        "http_status": tomato["status_code"],
        "disease": ((tb.get("disease") or {}).get("disease")),
        "rag_grounded": (tb.get("inference_meta") or {}).get("rag_grounded"),
        "guidance_available": (tb.get("inference_meta") or {}).get("guidance_available"),
        "sources_count": len(((tb.get("advisory") or {}).get("sources") or [])),
        "pesticide": (tb.get("advisory") or {}).get("pesticide_recommendation"),
        "total_api_ms": tomato["elapsed_ms"],
    }

    # Persist after crops as well (already have crops in report)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
