"""Pest object-detection package (primary IP102 YOLO11s)."""

from app.ml.pest.pest_detector import PestObjectDetector, pest_object_detector
from app.ml.pest.pest_registry import PRIMARY_PEST_MODEL_ID, primary_pest_spec

__all__ = [
    "PestObjectDetector",
    "pest_object_detector",
    "PRIMARY_PEST_MODEL_ID",
    "primary_pest_spec",
]
