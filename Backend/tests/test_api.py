import io
import os
import sys
from pathlib import Path

# Ensure Backend/ is on path when running from repo root or Backend/
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
os.environ["CORS_ORIGINS"] = "http://localhost:5173,http://127.0.0.1:5173"

from fastapi.testclient import TestClient
from PIL import Image
from app.main import app
from app.services.seed_data import seed_initial_data
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_data():
    import asyncio
    asyncio.run(seed_initial_data())


def _login(email: str, password: str = "cropshield123") -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "CropShield AI" in data["service"]
    assert data["disease_inference"] == "TEST_MOCK"
    assert "JWT" not in str(data).upper() or "SECRET" not in str(data).upper()
    assert "GROQ_API" not in str(data).upper()
    assert data.get("persistence_mode") in ("memory", "mongodb")


def test_auth_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "demo@cropshield.ai",
        "password": "cropshield123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "demo@cropshield.ai"
    assert data["user"]["role"] == "FARMER"


def test_diagnose_requires_auth():
    img = Image.new("RGB", (100, 100), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    response = client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf.jpg", buf, "image/jpeg")},
        data={"crop_hint": "Tomato"},
    )
    assert response.status_code == 401


def test_gatekeeper_rejection_for_non_crop():
    token = _login("demo@cropshield.ai")
    img = Image.new("RGB", (100, 100), color=(240, 240, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    response = client.post(
        "/api/v1/diagnose",
        files={"file": ("blank.jpg", buf, "image/jpeg")},
        data={"latitude": 19.9975, "longitude": 73.7898},
        headers=_auth(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert "No crop detected" in data["message"]


def test_diagnosis_pipeline_with_crop_leaf():
    token = _login("demo@cropshield.ai")
    img = Image.new("RGB", (128, 128), color=(34, 139, 34))
    for x in range(40, 60):
        for y in range(40, 60):
            img.putpixel((x, y), (139, 69, 19))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    response = client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf.jpg", buf, "image/jpeg")},
        data={"latitude": 19.9975, "longitude": 73.7898, "crop_hint": "Tomato"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["crop"] == "Tomato"
    assert "disease" in data
    assert "inference_meta" in data
    assert data["inference_meta"]["pest_mock_enabled"] is False
    assert data["pests"] == []  # USE_MOCK_PEST=false
    assert "advisory" in data


def test_farmer_cannot_access_admin_analytics():
    token = _login("demo@cropshield.ai")
    response = client.get("/api/v1/admin/stats", headers=_auth(token))
    assert response.status_code == 403


def test_admin_stats_real_counts():
    token = _login("admin@cropshield.ai")
    response = client.get("/api/v1/admin/stats", headers=_auth(token))
    assert response.status_code == 200
    data = response.json()
    assert data["is_demo_inflated"] is False
    assert data["total_analyses"] >= 1
    assert data["total_farmers"] >= 1
    # Must not contain the old inflated offsets
    assert data["total_analyses"] < 1000


def test_gis_hotspots_admin_only():
    farmer = _login("demo@cropshield.ai")
    denied = client.get("/api/v1/admin/hotspots", headers=_auth(farmer))
    assert denied.status_code == 403
    admin = _login("admin@cropshield.ai")
    ok = client.get("/api/v1/admin/hotspots", headers=_auth(admin))
    assert ok.status_code == 200
    data = ok.json()
    assert data["type"] == "FeatureCollection"


def test_register_cannot_self_elevate():
    response = client.post("/api/v1/auth/register", json={
        "email": "hacker@example.com",
        "password": "password123",
        "full_name": "Hacker",
        "role": "ADMIN",
    })
    assert response.status_code == 403


def test_assistant_asks_for_crop_when_missing():
    token = _login("demo@cropshield.ai")
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "How do I manage blight?"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "crop" in data["reply"].lower()


def test_assistant_with_crop_context():
    token = _login("demo@cropshield.ai")
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What should I monitor this week?", "crop_context": "Tomato"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    assert len(response.json()["reply"]) > 20


def test_production_startup_rejects_missing_jwt():
    from app.core.startup_checks import validate_runtime_settings
    from types import SimpleNamespace

    bad = SimpleNamespace(
        ENVIRONMENT="production",
        JWT_SECRET="",
        SEED_DEMO_DATA=False,
        ALLOW_DEMO_AUTH=False,
        USE_MOCK_AI=False,
        CORS_ORIGINS=["https://example.com"],
        USE_MOCK_PEST=False,
    )
    try:
        validate_runtime_settings(bad)
        assert False, "expected SystemExit"
    except SystemExit:
        pass


def test_production_startup_rejects_demo_seed_flag():
    from app.core.startup_checks import validate_runtime_settings
    from types import SimpleNamespace

    bad = SimpleNamespace(
        ENVIRONMENT="production",
        JWT_SECRET="a" * 40,
        SEED_DEMO_DATA=True,
        ALLOW_DEMO_AUTH=False,
        USE_MOCK_AI=False,
        CORS_ORIGINS=["https://example.com"],
        USE_MOCK_PEST=False,
    )
    try:
        validate_runtime_settings(bad)
        assert False, "expected SystemExit"
    except SystemExit:
        pass


def test_production_startup_rejects_mock_ai():
    from app.core.startup_checks import validate_runtime_settings
    from types import SimpleNamespace

    bad = SimpleNamespace(
        ENVIRONMENT="production",
        JWT_SECRET="a" * 40,
        SEED_DEMO_DATA=False,
        ALLOW_DEMO_AUTH=False,
        USE_MOCK_AI=True,
        CORS_ORIGINS=["https://example.com"],
        USE_MOCK_PEST=False,
    )
    try:
        validate_runtime_settings(bad)
        assert False, "expected SystemExit"
    except SystemExit:
        pass


def test_production_startup_rejects_demo_auth():
    from app.core.startup_checks import validate_runtime_settings
    from types import SimpleNamespace

    bad = SimpleNamespace(
        ENVIRONMENT="production",
        JWT_SECRET="a" * 40,
        SEED_DEMO_DATA=False,
        ALLOW_DEMO_AUTH=True,
        USE_MOCK_AI=False,
        CORS_ORIGINS=["https://example.com"],
        USE_MOCK_PEST=False,
    )
    try:
        validate_runtime_settings(bad)
        assert False, "expected SystemExit"
    except SystemExit:
        pass


def test_production_startup_rejects_empty_cors_and_wildcard():
    from app.core.startup_checks import validate_runtime_settings, FORBIDDEN_JWT_SECRETS
    from types import SimpleNamespace

    empty_cors = SimpleNamespace(
        ENVIRONMENT="production",
        JWT_SECRET="a" * 40,
        SEED_DEMO_DATA=False,
        ALLOW_DEMO_AUTH=False,
        USE_MOCK_AI=False,
        CORS_ORIGINS=[],
        USE_MOCK_PEST=False,
    )
    try:
        validate_runtime_settings(empty_cors)
        assert False, "expected SystemExit for empty CORS"
    except SystemExit:
        pass

    # Placeholder JWT from .env.example must be rejected
    assert "generate-a-long-random-secret-at-least-32-chars" in FORBIDDEN_JWT_SECRETS
    placeholder = SimpleNamespace(
        ENVIRONMENT="production",
        JWT_SECRET="generate-a-long-random-secret-at-least-32-chars",
        SEED_DEMO_DATA=False,
        ALLOW_DEMO_AUTH=False,
        USE_MOCK_AI=False,
        CORS_ORIGINS=["https://app.example.com"],
        USE_MOCK_PEST=False,
    )
    try:
        validate_runtime_settings(placeholder)
        assert False, "expected SystemExit for placeholder JWT"
    except SystemExit:
        pass


def test_production_startup_accepts_valid_config():
    from app.core.startup_checks import validate_runtime_settings
    from types import SimpleNamespace

    ok = SimpleNamespace(
        ENVIRONMENT="production",
        JWT_SECRET="prod-audit-test-secret-not-for-deploy-use-xx",
        SEED_DEMO_DATA=False,
        ALLOW_DEMO_AUTH=False,
        USE_MOCK_AI=False,
        CORS_ORIGINS=["https://farmer.example.com", "https://admin.example.com"],
        USE_MOCK_PEST=False,
    )
    validate_runtime_settings(ok)  # must not raise


def test_health_response_has_no_secrets():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    blob = response.text.lower()
    for needle in ("jwt", "secret", "gsk_", "mongodb://", "hf_token", "password", "bearer "):
        assert needle not in blob
    data = response.json()
    assert "JWT_SECRET" not in data
    assert "GROQ_API_KEY" not in data
    assert "MONGO_URI" not in data
