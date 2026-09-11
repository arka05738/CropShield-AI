"""
REAL_HF_SMOKE_TEST — loads verified Hugging Face models and runs real inference.

Does NOT use USE_MOCK_AI or heuristic disease output.
SMOKE TEST ≠ ACCURACY TEST (synthetic leaf image only).
"""
from __future__ import annotations

import io
import time

import pytest
from PIL import Image, ImageDraw

from app.ml.hf_crop_registry import build_crop_registry
from app.ml.hf_disease_classifier import hf_disease_classifier
from app.ml.hf_model_loader import load_transformers_classifier

pytestmark = pytest.mark.real_hf_smoke


def _sample_jpeg() -> bytes:
    img = Image.new("RGB", (224, 224), color=(34, 120, 40))
    d = ImageDraw.Draw(img)
    d.ellipse((40, 40, 180, 200), fill=(34, 120, 40))
    d.ellipse((70, 70, 110, 110), fill=(120, 80, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture(scope="module")
def sample_bytes():
    return _sample_jpeg()


def _assert_success(crop: str, expected_model_substr: str, sample_bytes: bytes):
    t0 = time.time()
    result = hf_disease_classifier.predict(sample_bytes, crop)
    elapsed = time.time() - t0
    assert result.status == "success", f"{crop}: {result.message}"
    assert result.raw_label, f"{crop}: missing raw_label"
    assert result.display_label, f"{crop}: missing display_label"
    assert result.confidence is not None and 0.0 <= result.confidence <= 1.0
    assert result.model_id and expected_model_substr in result.model_id
    assert result.provider == "huggingface"
    assert result.architecture
    print(
        f"REAL_HF_SMOKE_TEST PASS crop={crop} model={result.model_id} "
        f"raw={result.raw_label} conf={result.confidence} "
        f"load_s={result.load_seconds} infer_s={result.infer_seconds} wall_s={elapsed:.2f} "
        f"(SMOKE TEST != ACCURACY TEST)"
    )
    return result


def test_REAL_HF_SMOKE_plantvillage_grape(sample_bytes):
    _assert_success("Grape", "kimcomehome/plantvillage-vit-leaf-disease", sample_bytes)


def test_REAL_HF_SMOKE_plantvillage_tomato(sample_bytes):
    _assert_success("Tomato", "kimcomehome/plantvillage-vit-leaf-disease", sample_bytes)


def test_REAL_HF_SMOKE_sugarcane_lisha(sample_bytes):
    _assert_success("Sugarcane", "LishaV01/agriculture-crop-disease-detection", sample_bytes)


def test_REAL_HF_SMOKE_rice_wambugu(sample_bytes):
    _assert_success("Rice", "wambugu71/crop_leaf_diseases_vit", sample_bytes)


def test_REAL_HF_SMOKE_wheat_wambugu(sample_bytes):
    _assert_success("Wheat", "wambugu71/crop_leaf_diseases_vit", sample_bytes)


def test_REAL_HF_SMOKE_cotton_yaswanth(sample_bytes):
    _assert_success("Cotton", "YaswanthReddy23/ViT_Cotton", sample_bytes)


def test_REAL_HF_SMOKE_sunflower_yaswanth(sample_bytes):
    _assert_success("Sunflower", "YaswanthReddy23/ViT_Sunflower", sample_bytes)


def test_REAL_HF_SMOKE_model_load_timings():
    """Measure load (or cache hit) for each unique production model ID."""
    registry = build_crop_registry()
    unique_ids = sorted({spec.model_id for spec in registry.values()})
    timings = {}
    for mid in unique_ids:
        t0 = time.time()
        processor, model, id2label, architecture, load_s = load_transformers_classifier(mid)
        wall = round(time.time() - t0, 3)
        assert processor is not None and model is not None
        assert len(id2label) > 0
        timings[mid] = {
            "architecture": architecture,
            "classes": len(id2label),
            "reported_load_seconds": load_s,
            "wall_seconds": wall,
            "params": sum(p.numel() for p in model.parameters()),
        }
        print(f"REAL_HF_SMOKE_TEST LOAD {mid} -> {timings[mid]}")
    # plantvillage, lisha, wambugu, cotton, sunflower
    assert len(timings) == 5
