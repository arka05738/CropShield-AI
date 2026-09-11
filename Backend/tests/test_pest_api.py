"""
API tests for dedicated pest OD endpoint.

Uses mocked detector output so CI does not download YOLO weights.
Real weights are covered by test_pest_real_smoke.py.
"""
import io
import os
import sys
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

os.environ["JWT_SECRET"] = "test-jwt-secret-cropshield-32chars-min"
os.environ["ALLOW_DEMO_AUTH"] = "false"
os.environ["SEED_DEMO_DATA"] = "true"
os.environ["ENVIRONMENT"] = "development"
os.environ["USE_MOCK_WEATHER"] = "true"
os.environ["USE_MOCK_PEST"] = "false"
os.environ["USE_MOCK_AI"] = "true"
os.environ["USE_HF_DISEASE_MODEL"] = "false"
os.environ["USE_PEST_HF_MODEL"] = "true"
os.environ["PEST_CONFIDENCE_THRESHOLD"] = "0.25"
os.environ["CORS_ORIGINS"] = "http://localhost:5173,http://127.0.0.1:5173"

from fastapi.testclient import TestClient
from PIL import Image
import pytest

from app.main import app
from app.services.seed_data import seed_initial_data
from app.ml.pest.pest_schema import PestBBox, PestDetectionResult, PestObjectDetection

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_data():
    import asyncio

    asyncio.run(seed_initial_data())


def _login(email: str = "demo@cropshield.ai", password: str = "cropshield123") -> str:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _jpeg_bytes(color=(34, 139, 34)) -> bytes:
    img = Image.new("RGB", (320, 240), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_pest_detect_requires_auth():
    buf = io.BytesIO(_jpeg_bytes())
    r = client.post(
        "/api/v1/pests/detect",
        files={"file": ("leaf.jpg", buf, "image/jpeg")},
        data={"crop_hint": "Rice"},
    )
    assert r.status_code == 401


def test_pest_detect_no_detections_status():
    token = _login()
    empty = PestDetectionResult(
        detections=[],
        count=0,
        image_width=320,
        image_height=240,
        model_id="underdogquality/yolo11s-pest-detection",
        architecture="YOLO11s",
        inference_mode="huggingface_yolo",
        confidence_threshold=0.25,
        load_seconds=0.1,
        inference_ms=12.0,
        severity="none",
    )
    with patch("app.api.v1.pests.pest_object_detector.detect", return_value=empty):
        buf = io.BytesIO(_jpeg_bytes())
        r = client.post(
            "/api/v1/pests/detect",
            headers=_auth(token),
            files={"file": ("leaf.jpg", buf, "image/jpeg")},
            data={"crop_hint": "Rice"},
        )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "no_pest_detected"
    assert data["detections"] == []
    assert data["count"] == 0
    assert data["model"]["model_id"] == "underdogquality/yolo11s-pest-detection"
    assert "no pests exist" not in (data.get("advisory") or {}).get("condition_summary", "").lower()
    assert "without pests" in (data.get("advisory") or {}).get("condition_summary", "").lower()


def test_pest_detect_with_boxes_and_history():
    token = _login()
    det = PestDetectionResult(
        detections=[
            PestObjectDetection(
                pest="brown plant hopper",
                raw_label="brown plant hopper",
                confidence=0.81,
                bbox=PestBBox(x1=10, y1=20, x2=80, y2=90),
                class_id=7,
            )
        ],
        count=1,
        image_width=320,
        image_height=240,
        model_id="underdogquality/yolo11s-pest-detection",
        architecture="YOLO11s",
        inference_mode="huggingface_yolo",
        confidence_threshold=0.25,
        load_seconds=1.2,
        inference_ms=40.0,
        severity="low",
    )
    with patch("app.api.v1.pests.pest_object_detector.detect", return_value=det):
        buf = io.BytesIO(_jpeg_bytes())
        r = client.post(
            "/api/v1/pests/detect",
            headers=_auth(token),
            files={"file": ("leaf.jpg", buf, "image/jpeg")},
            data={"crop_hint": "Rice"},
        )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "pests_detected"
    assert data["count"] == 1
    assert data["detections"][0]["raw_label"] == "brown plant hopper"
    assert data["detections"][0]["bbox"]["x1"] == 10
    assert data["severity"] in ("low", "moderate", "high")
    assert "agronomic diagnosis" in data["severity_label"].lower()

    hist = client.get("/api/v1/pests/history", headers=_auth(token))
    assert hist.status_code == 200
    items = hist.json()["items"]
    assert any(i["id"] == data["id"] for i in items)


def test_farmer_cannot_access_admin_pests():
    token = _login("demo@cropshield.ai")
    r = client.get("/api/v1/admin/pests", headers=_auth(token))
    assert r.status_code == 403


def test_admin_pests_endpoint():
    token = _login("admin@cropshield.ai")
    r = client.get("/api/v1/admin/pests", headers=_auth(token))
    assert r.status_code == 200
    body = r.json()
    assert body.get("record_type") == "pest"
    assert "cases" in body


def test_diagnose_still_works_separately():
    """Disease diagnose must remain intact (pest OD is a separate endpoint)."""
    token = _login()
    buf = io.BytesIO(_jpeg_bytes())
    r = client.post(
        "/api/v1/diagnose",
        headers=_auth(token),
        files={"file": ("leaf.jpg", buf, "image/jpeg")},
        data={"crop_hint": "Tomato"},
    )
    assert r.status_code == 200, r.text
    assert "disease" in r.json()
