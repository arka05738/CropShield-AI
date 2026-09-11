"""
Hugging Face PlantVillage disease classifier.

Default model: kimcomehome/plantvillage-vit-leaf-disease
(ViT fine-tuned on PlantVillage — 38 crop/disease classes).

Does NOT use any models from outside this project directory.
Downloads weights from Hugging Face Hub into the local HF cache on first use.
"""
from __future__ import annotations

import io
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from app.core.config import settings

logger = logging.getLogger("cropshield.ml.hf_plantvillage")

# Canonical PlantVillage crop names → SIH crop names
HF_CROP_TO_SIH = {
    "apple": "Apple",
    "blueberry": "Blueberry",
    "cherry": "Cherry",
    "corn": "Maize",
    "maize": "Maize",
    "grape": "Grape",
    "orange": "Orange",
    "peach": "Peach",
    "pepper": "Pepper",
    "bell pepper": "Pepper",
    "potato": "Potato",
    "raspberry": "Raspberry",
    "soybean": "Soybean",
    "squash": "Squash",
    "strawberry": "Strawberry",
    "tomato": "Tomato",
}

# SIH crop hint → accepted HF label crop prefixes (lowercase)
SIH_CROP_TO_HF_PREFIXES = {
    "tomato": ["tomato"],
    "potato": ["potato"],
    "grape": ["grape"],
    "grapes": ["grape"],
    "maize": ["corn", "maize"],
    "corn": ["corn", "maize"],
    "apple": ["apple"],
    "cherry": ["cherry"],
    "peach": ["peach"],
    "pepper": ["pepper"],
    "strawberry": ["strawberry"],
    "soybean": ["soybean"],
    "orange": ["orange"],
    "blueberry": ["blueberry"],
    "raspberry": ["raspberry"],
    "squash": ["squash"],
}

DEFAULT_HF_MODEL_ID = "kimcomehome/plantvillage-vit-leaf-disease"


def _guess_pathogen(disease: str) -> str:
    d = disease.lower()
    if "healthy" in d or "fresh" in d:
        return "Healthy"
    if any(x in d for x in ("virus", "mosaic", "curl", "greening", "haunglongbing")):
        return "Viral"
    if "bacterial" in d:
        return "Bacterial"
    return "Fungal"


def parse_plantvillage_label(label: str) -> Tuple[str, str]:
    """
    Parse labels like 'Tomato___Early_blight' or 'Corn_(maize)___Common_rust_'.
    Returns (sih_crop, human_disease).
    """
    raw = (label or "").strip()
    if "___" in raw:
        crop_part, disease_part = raw.split("___", 1)
    elif "/" in raw:
        crop_part, disease_part = raw.split("/", 1)
    else:
        return "Unknown", raw.replace("_", " ").strip()

    crop_key = crop_part.lower().replace(",", " ").replace("(maize)", "maize")
    crop_key = " ".join(crop_key.replace("_", " ").split())
    # Normalize "pepper bell" / "corn maize"
    if "pepper" in crop_key:
        crop_key = "pepper"
    if "corn" in crop_key or crop_key == "maize":
        crop_key = "corn"

    sih_crop = HF_CROP_TO_SIH.get(crop_key, crop_part.replace("_", " ").title())
    disease = disease_part.replace("_", " ").strip()
    disease = " ".join(disease.split())
    if disease.lower() == "healthy":
        disease = "Healthy Crop"
    return sih_crop, disease


class HuggingFacePlantVillageClassifier:
    """Lazy-loaded HF image-classification pipeline for PlantVillage diseases."""

    def __init__(self) -> None:
        self.model_id = (
            getattr(settings, "HF_DISEASE_MODEL_ID", None)
            or os.getenv("HF_DISEASE_MODEL_ID")
            or DEFAULT_HF_MODEL_ID
        )
        self.enabled = bool(getattr(settings, "USE_HF_DISEASE_MODEL", True))
        self._pipe = None
        self._load_error: Optional[str] = None
        self.id2label: Dict[str, str] = {}
        self.loaded = False

    @property
    def available(self) -> bool:
        return bool(self.enabled) and self._pipe is not None and self._load_error is None

    def ensure_loaded(self) -> bool:
        if not self.enabled:
            self._load_error = "USE_HF_DISEASE_MODEL is false"
            return False
        if self._pipe is not None:
            return True
        if self._load_error and self.loaded is False and "failed" in (self._load_error or "").lower():
            # Allow retry only if never successfully attempted after code change
            pass

        try:
            from transformers import pipeline

            token = settings.HF_TOKEN or None
            kwargs: Dict[str, Any] = {
                "task": "image-classification",
                "model": self.model_id,
            }
            if token:
                kwargs["token"] = token

            # Prefer CPU for broader deploy compatibility; CUDA used if available
            device = -1
            try:
                import torch

                if torch.cuda.is_available():
                    device = 0
            except Exception:
                device = -1
            kwargs["device"] = device

            logger.info("Loading Hugging Face disease model: %s", self.model_id)
            self._pipe = pipeline(**kwargs)
            # Capture labels from model config when present
            model = getattr(self._pipe, "model", None)
            cfg = getattr(model, "config", None) if model is not None else None
            raw_map = getattr(cfg, "id2label", None) or {}
            self.id2label = {str(k): str(v) for k, v in dict(raw_map).items()}
            self.loaded = True
            self._load_error = None
            logger.info(
                "HF disease model ready (%s). Classes=%s",
                self.model_id,
                len(self.id2label) or "unknown",
            )
            return True
        except Exception as e:
            self._pipe = None
            self.loaded = False
            self._load_error = str(e)
            logger.warning("Hugging Face disease model unavailable: %s", e)
            return False

    def _crop_prefixes(self, crop_hint: Optional[str]) -> Optional[List[str]]:
        if not crop_hint:
            return None
        key = crop_hint.strip().lower()
        return SIH_CROP_TO_HF_PREFIXES.get(key)

    def supports_crop(self, crop_hint: Optional[str]) -> bool:
        if not crop_hint:
            return True  # can still run global top-1
        return self._crop_prefixes(crop_hint) is not None

    def predict(
        self,
        image_bytes: bytes,
        crop_hint: Optional[str] = None,
        top_k: int = 5,
    ) -> Optional[Dict[str, Any]]:
        """
        Returns dict with disease, pathogen_type, confidence, crop, label, alternatives
        or None if model unavailable / crop not covered.
        """
        if not self.ensure_loaded():
            return None

        prefixes = self._crop_prefixes(crop_hint)
        if crop_hint and prefixes is None:
            # Explicit crop not in PlantVillage coverage
            return {
                "covered": False,
                "crop": crop_hint,
                "disease": None,
                "confidence": 0.0,
                "note": (
                    f"Hugging Face PlantVillage model does not cover '{crop_hint}'. "
                    f"Covered crops include Tomato, Potato, Grape, Maize/Corn, Apple, etc."
                ),
            }

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results: List[Dict[str, Any]] = self._pipe(image, top_k=top_k)
        if not results:
            return None

        # Rank by score (pipeline already sorted); optionally filter by crop
        ranked = list(results)
        if prefixes:
            filtered = []
            for r in ranked:
                label = str(r.get("label", "")).lower()
                if any(p in label for p in prefixes):
                    filtered.append(r)
            if not filtered:
                return {
                    "covered": True,
                    "crop": crop_hint,
                    "disease": None,
                    "confidence": 0.0,
                    "note": (
                        f"No PlantVillage class matched crop '{crop_hint}' among top-{top_k} predictions. "
                        "Try a clearer leaf image or another crop hint."
                    ),
                    "raw_top": ranked[:3],
                }
            ranked = filtered

        best = ranked[0]
        label = str(best.get("label", ""))
        score = float(best.get("score", 0.0))
        # Softmax/pipeline score already; treat as confidence. Argmax ≡ top-1.
        sih_crop, disease = parse_plantvillage_label(label)
        pathogen = _guess_pathogen(disease)

        alternatives = []
        for r in ranked[1:4]:
            c, d = parse_plantvillage_label(str(r.get("label", "")))
            alternatives.append(
                {"crop": c, "disease": d, "confidence": round(float(r.get("score", 0.0)), 4)}
            )

        return {
            "covered": True,
            "crop": crop_hint or sih_crop,
            "detected_crop": sih_crop,
            "disease": disease,
            "pathogen_type": pathogen,
            "confidence": round(score, 4),
            "label": label,
            "model_id": self.model_id,
            "inference_mode": "huggingface_trained",
            "alternatives": alternatives,
            "note": (
                f"Prediction from Hugging Face model '{self.model_id}' (PlantVillage). "
                "Image-level result; not a field-wide infestation measurement."
            ),
        }


hf_plantvillage_classifier = HuggingFacePlantVillageClassifier()
