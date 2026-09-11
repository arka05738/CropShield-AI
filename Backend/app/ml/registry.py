from typing import List, Dict, Any
from app.core.config import settings
from app.ml.hf_crop_registry import ALTERNATIVE_MODELS, build_crop_registry, UNSUPPORTED_CROPS
from app.ml.pest.pest_registry import (
    BACKUP_PEST_MODEL_ID,
    PRIMARY_PEST_MODEL_ID,
    SPECIALIST_FAW_MODEL_ID,
    primary_pest_spec,
)


class ModelRegistry:
    """
    Admin-facing registry metadata — honest about multi-model HF routing.
    """

    def __init__(self):
        pest_spec = primary_pest_spec()
        pest_hf_on = bool(settings.USE_PEST_HF_MODEL) and not settings.USE_MOCK_PEST
        pest_status = (
            "ACTIVE"
            if pest_hf_on or settings.USE_MOCK_PEST or settings.PEST_MODEL_PATH
            else "UNAVAILABLE"
        )
        pest_mode = (
            "huggingface_yolo"
            if pest_hf_on
            else ("mock" if settings.USE_MOCK_PEST else "unavailable")
        )
        hf_on = bool(settings.USE_HF_DISEASE_MODEL) and not settings.USE_MOCK_AI
        crop_map = build_crop_registry() if hf_on else {}
        routing = {
            crop: {"model_id": spec.model_id, "key": spec.key}
            for crop, spec in crop_map.items()
        }

        self.models: List[Dict[str, Any]] = [
            {
                "id": "gatekeeper_v1",
                "task": "Crop Presence Detection",
                "model_name": "ExG-BioFilter",
                "provider": "Local Edge Heuristic",
                "version": "1.2.0",
                "threshold": 0.60,
                "status": "ACTIVE",
                "inference_mode": "heuristic",
                "supported_classes": ["Vegetative Crop", "Non-Crop"],
            },
            {
                "id": "crop_classifier_v2",
                "task": "Crop Identification",
                "model_name": "heuristic-color-hash",
                "provider": "Local Heuristic",
                "version": "2.1.0",
                "threshold": 0.70,
                "status": "ACTIVE",
                "inference_mode": "heuristic",
                "supported_classes": list(routing.keys()) + sorted(UNSUPPORTED_CROPS),
                "note": "Prefer farmer crop_hint. Disease routing uses verified HF crop registry.",
            },
            {
                "id": "disease_classifier_v3",
                "task": "Disease Detection (multi-model HF)",
                "model_name": "huggingface-multi-model-registry",
                "provider": "Hugging Face Hub",
                "version": "3.0.0",
                "threshold": 0.65,
                "status": "ACTIVE" if hf_on else "UNAVAILABLE",
                "inference_mode": "huggingface_trained" if hf_on else "unavailable",
                "supported_classes": list(routing.keys()),
                "crop_routing": routing if hf_on else {},
                "unsupported_crops": sorted(UNSUPPORTED_CROPS),
                "model_ids": {
                    "plantvillage": settings.HF_MODEL_PLANTVILLAGE,
                    "sugarcane": settings.HF_MODEL_SUGARCANE,
                    "rice": settings.HF_MODEL_RICE,
                    "wheat": settings.HF_MODEL_WHEAT,
                    "cotton": settings.HF_MODEL_COTTON,
                    "sunflower": settings.HF_MODEL_SUNFLOWER,
                },
                "alternatives_not_in_production": ALTERNATIVE_MODELS,
                "note": (
                    "Verified routing only. Unknown crops → model_unavailable. "
                    "No heuristic disease fallback. Arko007 not used (NC license / heavy). "
                    "Cotton/Sunflower are single-crop specialists (labels omit crop token)."
                    if hf_on
                    else "HF disabled or USE_MOCK_AI."
                ),
            },
            {
                "id": "pest_detector",
                "task": "Pest Bounding Box Detection",
                "model_name": pest_spec.model_id if pest_hf_on else "pest-detector",
                "provider": "Hugging Face Hub + Ultralytics" if pest_hf_on else "Abstraction",
                "version": "2.0.0",
                "threshold": float(settings.PEST_CONFIDENCE_THRESHOLD),
                "status": pest_status,
                "inference_mode": pest_mode,
                "model_id": pest_spec.model_id,
                "supported_classes_count": 102,
                "endpoint": "POST /api/v1/pests/detect",
                "backup_not_integrated": BACKUP_PEST_MODEL_ID,
                "specialist_not_integrated": SPECIALIST_FAW_MODEL_ID,
                "default_primary": PRIMARY_PEST_MODEL_ID,
                "note": (
                    "Primary OD only: underdogquality/yolo11s-pest-detection. "
                    "Threshold is detection filter, not accuracy. "
                    "Author-reported val mAP@0.5=0.815 is NOT CropShield accuracy. "
                    "Separate pest history; disease /diagnose unchanged."
                    if pest_hf_on
                    else "Enable USE_PEST_HF_MODEL=true (default) with ultralytics installed."
                ),
            },
            {
                "id": "embedding_hash",
                "task": "Agricultural Knowledge Embeddings",
                "model_name": "FastAgriculturalEmbedding-hash64",
                "provider": "ChromaDB + local hash embedding",
                "version": "1.0.0",
                "threshold": 0.0,
                "status": "ACTIVE",
                "inference_mode": "hash_embedding",
                "supported_classes": ["ICAR POP curated records"],
                "note": "Not MiniLM. Hash embedding for demo retrieval.",
            },
        ]

    def get_all(self) -> List[Dict[str, Any]]:
        return self.models

    def update_threshold(self, model_id: str, new_threshold: float) -> bool:
        for m in self.models:
            if m["id"] == model_id:
                m["threshold"] = new_threshold
                return True
        return False


model_registry = ModelRegistry()
