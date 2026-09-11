"""
Disease classification service — multi-model Hugging Face registry.

Production: verified HF models only. No heuristic disease names.
USE_MOCK_AI: isolated automated-test stub only (blocked in production startup).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.core.config import settings
from app.models.schemas import DiseasePrediction

logger = logging.getLogger("cropshield.ml.disease")

UNAVAILABLE_MSG = (
    "No verified Hugging Face disease model is currently available for this crop."
)


def _unavailable(
    crop: str,
    reason: str,
    model_name: Optional[str] = None,
    architecture: Optional[str] = None,
) -> DiseasePrediction:
    return DiseasePrediction(
        disease=None,
        pathogen_type="Unknown",
        confidence=None,
        description=reason or UNAVAILABLE_MSG,
        inference_mode="unavailable",
        model_name=model_name,
        note=reason or UNAVAILABLE_MSG,
        raw_label=None,
        display_label=None,
        model_provider="huggingface",
        model_architecture=architecture,
    )


class DiseaseModel:
    def __init__(
        self,
        model_name: str = "huggingface-multi-model",
        version: str = "3.0.0",
        confidence_threshold: float = 0.65,
    ):
        self.model_name = model_name
        self.version = version
        self.confidence_threshold = confidence_threshold
        self.inference_mode = "huggingface_trained"
        self.last_hf_meta: Optional[Dict[str, Any]] = None

    def _test_only_mock(self, crop: str) -> DiseasePrediction:
        return DiseasePrediction(
            disease="Healthy Crop",
            pathogen_type="Healthy",
            confidence=0.9,
            description="TEST-ONLY mock disease result (USE_MOCK_AI=true). Not a real model prediction.",
            inference_mode="mock",
            model_name="test-mock-disease",
            note="Isolated to automated tests via USE_MOCK_AI.",
            raw_label="mock_healthy",
            display_label="Healthy Crop",
            model_provider="test",
            model_architecture=None,
        )

    def inference(self, image_bytes: bytes, crop: str) -> DiseasePrediction:
        self.last_hf_meta = None

        if settings.USE_MOCK_AI:
            return self._test_only_mock(crop)

        if not getattr(settings, "USE_HF_DISEASE_MODEL", True):
            return _unavailable(
                crop,
                "USE_HF_DISEASE_MODEL is false. Enable Hugging Face disease inference to diagnose.",
                model_name="disabled",
            )

        try:
            from app.ml.hf_disease_classifier import hf_disease_classifier

            result = hf_disease_classifier.predict(image_bytes, crop)
        except Exception as e:
            logger.warning("HF disease path failed: %s", e)
            return _unavailable(crop, f"Hugging Face disease model error: {e}", model_name="error")

        self.last_hf_meta = {
            "status": result.status,
            "model_id": result.model_id,
            "architecture": result.architecture,
            "raw_label": result.raw_label,
            "display_label": result.display_label,
            "confidence": result.confidence,
            "load_seconds": result.load_seconds,
            "infer_seconds": result.infer_seconds,
            "alternatives": result.alternatives,
        }

        if result.status != "success" or result.raw_label is None or result.confidence is None:
            return _unavailable(
                crop,
                result.message or UNAVAILABLE_MSG,
                model_name=result.model_id,
                architecture=result.architecture,
            )

        low_conf_note = ""
        if result.confidence < self.confidence_threshold:
            low_conf_note = (
                f" Confidence {result.confidence:.2f} is below threshold "
                f"{self.confidence_threshold}. Retake a clearer leaf photo or request expert validation."
            )

        desc = (
            f"Hugging Face prediction raw_label='{result.raw_label}' "
            f"via model '{result.model_id}'."
            f"{low_conf_note}"
        )

        return DiseasePrediction(
            disease=result.display_label or result.raw_label,
            pathogen_type=result.pathogen_type,
            confidence=result.confidence,
            description=desc,
            inference_mode="huggingface_trained",
            model_name=result.model_id,
            note=(result.message or "") + low_conf_note,
            raw_label=result.raw_label,
            display_label=result.display_label,
            model_provider="huggingface",
            model_architecture=result.architecture,
        )


disease_model = DiseaseModel()
