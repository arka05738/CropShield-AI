"""
Verified crop → Hugging Face model routing.

Only crops with verified label evidence are mapped.
Unknown / unlisted crops → model_unavailable (no heuristic disease).
"""
from __future__ import annotations

from typing import Dict, Optional, Set

from app.core.config import settings
from app.ml.prediction_schema import HFModelSpec

DEFAULT_PLANTVILLAGE = "kimcomehome/plantvillage-vit-leaf-disease"
DEFAULT_SUGARCANE = "LishaV01/agriculture-crop-disease-detection"
DEFAULT_RICE_WHEAT = "wambugu71/crop_leaf_diseases_vit"
DEFAULT_COTTON = "YaswanthReddy23/ViT_Cotton"
DEFAULT_SUNFLOWER = "YaswanthReddy23/ViT_Sunflower"

# Alternatives (documented only — not used in production routing)
ALTERNATIVE_MODELS = {
    "sugarcane_alt_lisha_also_covers_rice_wheat": "LishaV01/agriculture-crop-disease-detection",
    "multi_crop_timm_nc_license": "Arko007/nfnet-f1-plant-disease",
}


def _pv_id() -> str:
    return (
        getattr(settings, "HF_MODEL_PLANTVILLAGE", None)
        or getattr(settings, "HF_DISEASE_MODEL_ID", None)
        or DEFAULT_PLANTVILLAGE
    )


def _sugar_id() -> str:
    return getattr(settings, "HF_MODEL_SUGARCANE", None) or DEFAULT_SUGARCANE


def _rice_id() -> str:
    return getattr(settings, "HF_MODEL_RICE", None) or DEFAULT_RICE_WHEAT


def _wheat_id() -> str:
    return getattr(settings, "HF_MODEL_WHEAT", None) or DEFAULT_RICE_WHEAT


def _cotton_id() -> str:
    return getattr(settings, "HF_MODEL_COTTON", None) or DEFAULT_COTTON


def _sunflower_id() -> str:
    return getattr(settings, "HF_MODEL_SUNFLOWER", None) or DEFAULT_SUNFLOWER


def build_crop_registry() -> Dict[str, HFModelSpec]:
    pv = _pv_id()
    sugar = _sugar_id()
    rice = _rice_id()
    wheat = _wheat_id()
    cotton = _cotton_id()
    sunflower = _sunflower_id()

    plantvillage = lambda tokens: HFModelSpec(
        key="plantvillage",
        model_id=pv,
        framework="transformers",
        architecture="ViTForImageClassification",
        crop_filter_tokens=tokens,
        notes="Verified PlantVillage 38-class model",
    )

    return {
        # PlantVillage-verified crops
        "Grape": plantvillage(["grape"]),
        "Tomato": plantvillage(["tomato"]),
        "Potato": plantvillage(["potato"]),
        "Maize": plantvillage(["corn", "maize"]),
        "Corn": plantvillage(["corn", "maize"]),
        "Apple": plantvillage(["apple"]),
        "Cherry": plantvillage(["cherry"]),
        "Peach": plantvillage(["peach"]),
        "Pepper": plantvillage(["pepper"]),
        "Strawberry": plantvillage(["strawberry"]),
        "Orange": plantvillage(["orange"]),
        "Blueberry": plantvillage(["blueberry"]),
        "Raspberry": plantvillage(["raspberry"]),
        "Soybean": plantvillage(["soybean"]),
        "Squash": plantvillage(["squash"]),
        # Specialized verified models
        "Sugarcane": HFModelSpec(
            key="sugarcane",
            model_id=sugar,
            framework="transformers",
            architecture="ViTForImageClassification",
            crop_filter_tokens=["sugarcane"],
            notes="Verified LishaV01 sugarcane labels",
        ),
        "Rice": HFModelSpec(
            key="rice",
            model_id=rice,
            framework="transformers",
            architecture="ViTForImageClassification",
            crop_filter_tokens=["rice"],
            notes="Verified wambugu71 rice labels",
        ),
        "Wheat": HFModelSpec(
            key="wheat",
            model_id=wheat,
            framework="transformers",
            architecture="ViTForImageClassification",
            crop_filter_tokens=["wheat"],
            notes="Verified wambugu71 wheat labels",
        ),
        # Single-crop specialists: labels lack crop token — empty filter = use all classes
        "Cotton": HFModelSpec(
            key="cotton",
            model_id=cotton,
            framework="transformers",
            architecture="ViTForImageClassification",
            crop_filter_tokens=[],
            notes=(
                "Verified YaswanthReddy23/ViT_Cotton. Labels omit 'cotton' token; "
                "crop context from crop_hint. Apache-2.0."
            ),
        ),
        "Sunflower": HFModelSpec(
            key="sunflower",
            model_id=sunflower,
            framework="transformers",
            architecture="ViTForImageClassification",
            crop_filter_tokens=[],
            notes=(
                "Verified YaswanthReddy23/ViT_Sunflower. Labels omit 'sunflower' token; "
                "crop context from crop_hint. Apache-2.0. Metric conflict on Hub — "
                "no project accuracy claimed."
            ),
        ),
    }


# Crops we explicitly document as unsupported for disease AI (not in registry).
# Unknown crops also resolve to unavailable via missing registry entry.
UNSUPPORTED_CROPS: Set[str] = {"Millet", "Sorghum", "Chickpea"}


def normalize_crop(crop: Optional[str]) -> str:
    if not crop:
        return ""
    c = crop.strip()
    aliases = {
        "grapes": "Grape",
        "grape": "Grape",
        "maize": "Maize",
        "corn": "Corn",
        "bell pepper": "Pepper",
        "chilli": "Pepper",
        "chili": "Pepper",
        "sugar cane": "Sugarcane",
        "sugarcane": "Sugarcane",
        "cotton": "Cotton",
        "sunflower": "Sunflower",
        "sun flower": "Sunflower",
    }
    key = c.lower()
    if key in aliases:
        return aliases[key]
    return c.title() if c else ""


def resolve_spec(crop: Optional[str]) -> Optional[HFModelSpec]:
    """Return HFModelSpec or None if unsupported / unknown."""
    name = normalize_crop(crop)
    if not name:
        return None
    if name in UNSUPPORTED_CROPS:
        return None
    registry = build_crop_registry()
    return registry.get(name)


def is_explicitly_unsupported(crop: Optional[str]) -> bool:
    name = normalize_crop(crop)
    if not name:
        return True
    if name in UNSUPPORTED_CROPS:
        return True
    return name not in build_crop_registry()
