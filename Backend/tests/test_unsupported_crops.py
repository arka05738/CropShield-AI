"""
UNSUPPORTED-CROP TESTS — no HF download required.
Unknown / explicitly unsupported crops must return model_unavailable with null fields.
Cotton and Sunflower are now SUPPORTED and must NOT use this path.
"""
from __future__ import annotations

import io

from PIL import Image

from app.core.config import settings
from app.ml.disease_classifier import DiseaseModel
from app.ml.hf_crop_registry import resolve_spec
from app.ml.hf_disease_classifier import hf_disease_classifier


def _green_jpeg() -> bytes:
    img = Image.new("RGB", (128, 128), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_millet_classifier_unavailable():
    result = hf_disease_classifier.predict(_green_jpeg(), "Millet")
    assert result.status == "model_unavailable"
    assert result.raw_label is None
    assert result.display_label is None
    assert result.confidence is None
    assert result.model_id is None
    assert "available for this crop" in (result.message or "").lower()


def test_sorghum_classifier_unavailable():
    result = hf_disease_classifier.predict(_green_jpeg(), "Sorghum")
    assert result.status == "model_unavailable"
    assert result.confidence is None
    assert result.raw_label is None


def test_disease_model_maps_unsupported_to_null_fields(monkeypatch):
    monkeypatch.setattr(settings, "USE_MOCK_AI", False)
    monkeypatch.setattr(settings, "USE_HF_DISEASE_MODEL", True)
    model = DiseaseModel()
    pred = model.inference(_green_jpeg(), "Millet")
    assert pred.inference_mode == "unavailable"
    assert pred.disease is None
    assert pred.confidence is None
    assert pred.raw_label is None


def test_cotton_and_sunflower_are_registered():
    assert resolve_spec("Cotton") is not None
    assert resolve_spec("Sunflower") is not None
    assert resolve_spec("Cotton").model_id == "YaswanthReddy23/ViT_Cotton" or (
        "ViT_Cotton" in resolve_spec("Cotton").model_id
    )
    assert "ViT_Sunflower" in resolve_spec("Sunflower").model_id
