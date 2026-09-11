"""
Pest detector registry — primary model only for this integration step.

Backup / specialist IDs are documented but not loaded.
"""
from __future__ import annotations

from app.core.config import settings
from app.ml.pest.pest_schema import PestModelSpec

# Documented but NOT integrated in this step
BACKUP_PEST_MODEL_ID = "Mustafa5645344/insect-detection-yolov8"
SPECIALIST_FAW_MODEL_ID = "ndunge23/SambaGuard-v2"

PRIMARY_PEST_MODEL_ID = "underdogquality/yolo11s-pest-detection"


def primary_pest_spec() -> PestModelSpec:
    model_id = (settings.PEST_HF_MODEL_ID or PRIMARY_PEST_MODEL_ID).strip()
    return PestModelSpec(
        key="primary_ip102_yolo11s",
        model_id=model_id,
        architecture="YOLO11s",
        provider="huggingface",
        task="object-detection",
        class_count=102,
        note=(
            "IP102 pest object detector. Author-reported validation mAP@0.5=0.815 "
            "is NOT CropShield accuracy. Backup/specialist models are not loaded."
        ),
    )
