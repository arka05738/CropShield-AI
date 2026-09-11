"""
Real pest YOLO smoke test — loads underdogquality/yolo11s-pest-detection.

Does NOT use USE_MOCK_AI / USE_MOCK_PEST.
May return zero detections on a synthetic leaf (still valid):
MODEL LOADED + INFERENCE EXECUTED + ZERO DETECTIONS

If SambaGuard training mosaic is available under docs/_pest_research, uses it
for a higher chance of non-zero boxes (still not accuracy evidence).
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent
sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("JWT_SECRET", "test-jwt-secret-cropshield-32chars-min")
os.environ["USE_MOCK_AI"] = "false"
os.environ["USE_MOCK_PEST"] = "false"
os.environ["USE_PEST_HF_MODEL"] = "true"
os.environ["PEST_HF_MODEL_ID"] = "underdogquality/yolo11s-pest-detection"
os.environ["PEST_CONFIDENCE_THRESHOLD"] = "0.25"
os.environ["ENVIRONMENT"] = "development"

# Prefer research weights if already downloaded (avoids re-download)
_RESEARCH_WEIGHTS = (
    PROJECT_ROOT
    / "docs"
    / "_pest_research"
    / "weights"
    / "underdogquality__yolo11s-pest-detection"
    / "best.pt"
)
if _RESEARCH_WEIGHTS.is_file() and _RESEARCH_WEIGHTS.stat().st_size > 1_000_000:
    os.environ["PEST_MODEL_PATH"] = str(_RESEARCH_WEIGHTS)

from PIL import Image, ImageDraw  # noqa: E402

from app.ml.pest.pest_detector import PestObjectDetector  # noqa: E402
from app.ml.pest.pest_model_loader import load_pest_yolo  # noqa: E402
from app.ml.pest.pest_registry import PRIMARY_PEST_MODEL_ID  # noqa: E402


def _synthetic_leaf_bytes() -> bytes:
    img = Image.new("RGB", (640, 640), (20, 110, 35))
    d = ImageDraw.Draw(img)
    d.ellipse((180, 160, 460, 480), fill=(34, 140, 40))
    import io

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def _prefer_sample_bytes() -> tuple[bytes, str]:
    sample = (
        PROJECT_ROOT
        / "docs"
        / "_pest_research"
        / "samples"
        / "training_samples"
        / "train_batch0.jpg"
    )
    if sample.is_file():
        return sample.read_bytes(), f"real_sample:{sample.name}"
    return _synthetic_leaf_bytes(), "SMOKE TEST ONLY — synthetic leaf"


@pytest.mark.integration
def test_real_pest_model_load_and_inference():
    try:
        import ultralytics  # noqa: F401
    except ImportError:
        pytest.skip("ultralytics not installed")

    t0 = time.perf_counter()
    model, names, arch, load_s = load_pest_yolo(PRIMARY_PEST_MODEL_ID)
    first_load = time.perf_counter() - t0
    assert model is not None
    assert len(names) == 102
    assert arch

    # Warm cache path
    t1 = time.perf_counter()
    _, _, _, load_s2 = load_pest_yolo(PRIMARY_PEST_MODEL_ID)
    warm_load = time.perf_counter() - t1
    assert warm_load < first_load or warm_load < 0.5

    detector = PestObjectDetector()
    image_bytes, note = _prefer_sample_bytes()
    result = detector.detect(image_bytes, crop_hint="Rice")

    assert result.inference_mode == "huggingface_yolo"
    assert result.model_id.endswith("yolo11s-pest-detection") or "yolo11s-pest-detection" in result.model_id
    assert result.error is None
    assert result.image_width > 0 and result.image_height > 0
    assert result.inference_ms is not None
    assert result.count == len(result.detections)

    if result.count == 0:
        # Valid real smoke outcome
        assert result.severity == "none"
        print(
            "MODEL LOADED + INFERENCE EXECUTED + ZERO DETECTIONS |",
            note,
            f"load_s={load_s} infer_ms={result.inference_ms}",
        )
    else:
        d0 = result.detections[0]
        assert d0.raw_label
        assert d0.pest == d0.raw_label
        assert 0.0 <= d0.confidence <= 1.0
        assert d0.bbox.x2 >= d0.bbox.x1
        assert d0.bbox.y2 >= d0.bbox.y1
        print(
            "NONZERO DETECTIONS",
            result.count,
            d0.raw_label,
            d0.confidence,
            d0.bbox.to_dict(),
            note,
            f"infer_ms={result.inference_ms}",
        )

    # Timing / memory rough note (not a hard assert)
    print(
        f"PERF first_load_s={round(first_load, 3)} cached_load_s={round(warm_load, 3)} "
        f"infer_ms={result.inference_ms} classes={len(names)}"
    )
