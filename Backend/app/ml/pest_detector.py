"""
Pest detection service abstraction.

No trained YOLO weights ship with this repository.
- Default: return empty detections (do not fabricate production pest results).
- USE_MOCK_PEST=true: heuristic demo detections clearly labeled is_mock=True.
- PEST_MODEL_PATH + ultralytics (optional future): load real weights when provided.
"""
import io
import logging
from typing import List, Optional
from PIL import Image
import numpy as np
from app.core.config import settings
from app.models.schemas import PestDetectionItem, BoundingBox

logger = logging.getLogger("cropshield.ml.pest")

PEST_TAXONOMY = {
    "Tomato": [
        {"name": "Aphid", "sci": "Aphis gossypii", "default_sev": "Moderate"},
        {"name": "Whitefly", "sci": "Bemisia tabaci", "default_sev": "High"},
    ],
    "Rice": [
        {"name": "Yellow Stem Borer", "sci": "Scirpophaga incertulas", "default_sev": "Severe"},
        {"name": "Brown Plant Hopper", "sci": "Nilaparvata lugens", "default_sev": "High"},
    ],
    "Cotton": [
        {"name": "American Bollworm", "sci": "Helicoverpa armigera", "default_sev": "Severe"},
        {"name": "Pink Bollworm", "sci": "Pectinophora gossypiella", "default_sev": "Severe"},
    ],
    "Potato": [
        {"name": "Potato Tuber Moth", "sci": "Phthorimaea operculella", "default_sev": "High"},
    ],
    "Maize": [
        {"name": "Fall Armyworm", "sci": "Spodoptera frugiperda", "default_sev": "Severe"},
    ],
    "Wheat": [
        {"name": "Wheat Aphid", "sci": "Rhopalosiphum padi", "default_sev": "Moderate"},
    ],
}


class PestDetectionService:
    """
    Pluggable pest detector.
    Extension point for a real YOLO model via PEST_MODEL_PATH.
    """

    def __init__(self):
        self.model_name = settings.PEST_HF_MODEL_ID if settings.USE_PEST_HF_MODEL else "pest-detector-unavailable"
        self.threshold = 0.50
        self._yolo = None
        self.mode = "huggingface_yolo11s" if settings.USE_PEST_HF_MODEL else "unavailable"
        self._try_load_trained_model()

    def _try_load_trained_model(self) -> None:
        path = settings.PEST_MODEL_PATH
        if not path:
            return
        try:
            from ultralytics import YOLO  # optional dependency

            self._yolo = YOLO(path)
            self.model_name = f"yolo:{path}"
            self.mode = "trained"
            logger.info(f"Loaded pest model from {path}")
        except Exception as e:
            logger.warning(f"Could not load pest model at {path}: {e}")
            self._yolo = None
            self.mode = "unavailable"

    def detect(self, image_bytes: bytes, crop: str) -> List[PestDetectionItem]:
        if self._yolo is not None:
            return self._detect_yolo(image_bytes, crop)

        if settings.USE_MOCK_PEST:
            return self._detect_mock_heuristic(image_bytes, crop)

        # Production-safe default: no fabricated pest predictions
        logger.info("Pest detection skipped (no trained model; USE_MOCK_PEST=false)")
        return []

    def _detect_yolo(self, image_bytes: bytes, crop: str) -> List[PestDetectionItem]:
        # Placeholder for real YOLO integration — returns empty until wired with class maps
        logger.warning("YOLO pest model loaded but class mapping not configured; returning empty")
        return []

    def _detect_mock_heuristic(self, image_bytes: bytes, crop: str) -> List[PestDetectionItem]:
        """DEMO ONLY — clearly labeled mock detections."""
        note = "MOCK / DEMO pest detection (USE_MOCK_PEST=true). Not a trained YOLO result."
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            np_img = np.array(image.resize((64, 64)), dtype=np.float32)
            high_freq_dots = np.std(np_img, axis=2) > 40
            density = float(np.mean(high_freq_dots))
            crop_pests = PEST_TAXONOMY.get(crop, PEST_TAXONOMY.get("Tomato", []))
            if not crop_pests or density <= 0.08:
                return []

            primary = crop_pests[0]
            return [
                PestDetectionItem(
                    name=primary["name"],
                    scientific_name=primary["sci"],
                    confidence=round(min(0.9, 0.7 + density), 2),
                    bbox=BoundingBox(x=0.28, y=0.22, width=0.26, height=0.24),
                    severity=primary["default_sev"],
                    is_mock=True,
                    inference_mode="mock",
                    note=note,
                )
            ]
        except Exception as e:
            logger.error(f"Mock pest detection error: {e}")
            return []


# Backwards-compatible name
PestDetector = PestDetectionService
pest_detector = PestDetectionService()
