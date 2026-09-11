"""
Multi-model Hugging Face disease classifier with verified crop routing.

No heuristic disease names. No Arko007 in production path.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import torch

from app.ml.hf_crop_registry import (
    is_explicitly_unsupported,
    normalize_crop,
    resolve_spec,
)
from app.ml.hf_model_loader import last_load_error, load_transformers_classifier
from app.ml.prediction_schema import HFPredictionResult
from app.ml.preprocessing import bytes_to_rgb_pil

logger = logging.getLogger("cropshield.ml.hf_disease")

UNAVAILABLE_MESSAGE = (
    "No verified Hugging Face disease model is currently available for this crop."
)


def _guess_pathogen(label: str) -> str:
    d = (label or "").lower()
    if "healthy" in d or "fresh" in d:
        return "Healthy"
    if any(x in d for x in ("virus", "mosaic", "curl", "greening", "haunglongbing")):
        return "Viral"
    if "bacterial" in d:
        return "Bacterial"
    if d.strip() in ("invalid",) or "invalid" in d:
        return "Unknown"
    return "Fungal"


def _display_from_raw(raw: str) -> str:
    """Light display normalization — preserves meaning; raw_label kept separately."""
    text = (raw or "").strip()
    if "___" in text:
        text = text.split("___", 1)[1]
    elif "__" in text:
        text = text.split("__", 1)[1]
    else:
        low = text.lower()
        for prefix in ("sugarcane_", "rice_", "wheat_", "corn_", "potato_"):
            if low.startswith(prefix):
                text = text[len(prefix) :]
                break
    text = text.replace("_", " ").strip()
    text = " ".join(text.split())
    if text.lower() in ("healthy", "healthy leaf"):
        return "Healthy Crop"
    return text


def _label_matches_crop(label: str, tokens: List[str]) -> bool:
    low = (label or "").lower().replace("_", " ")
    return any(tok in low for tok in tokens)


def _rank_predictions(
    probs: torch.Tensor,
    id2label: Dict[str, str],
    tokens: List[str],
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """
    Return [(label, score), ...] .
    Empty tokens → single-crop specialist: use global top-k (all classes belong to crop).
    Non-empty tokens → multi-crop model: keep only labels matching crop tokens.
    """
    k = min(max(top_k, 5), probs.numel())
    values, indices = torch.topk(probs, k=k)
    ranked: List[Tuple[str, float]] = []
    for v, i in zip(values.tolist(), indices.tolist()):
        lab = id2label.get(str(int(i)), str(int(i)))
        ranked.append((lab, float(v)))

    if not tokens:
        return ranked

    filtered = [(lab, sc) for lab, sc in ranked if _label_matches_crop(lab, tokens)]
    if filtered:
        return filtered

    # Fall back: scan full distribution for crop-matching classes
    full: List[Tuple[str, float]] = []
    for idx in range(probs.numel()):
        lab = id2label.get(str(idx), str(idx))
        if _label_matches_crop(lab, tokens):
            full.append((lab, float(probs[idx].item())))
    full.sort(key=lambda x: x[1], reverse=True)
    return full


class HuggingFaceDiseaseClassifier:
    def predict(self, image_bytes: bytes, crop: str) -> HFPredictionResult:
        crop_name = normalize_crop(crop)

        if is_explicitly_unsupported(crop_name):
            return HFPredictionResult(
                status="model_unavailable",
                crop=crop_name or crop,
                raw_label=None,
                display_label=None,
                confidence=None,
                model_id=None,
                architecture=None,
                message=UNAVAILABLE_MESSAGE,
            )

        spec = resolve_spec(crop_name)
        if spec is None:
            return HFPredictionResult(
                status="model_unavailable",
                crop=crop_name or crop or "Unknown",
                raw_label=None,
                display_label=None,
                confidence=None,
                model_id=None,
                architecture=None,
                message=UNAVAILABLE_MESSAGE,
            )

        try:
            processor, model, id2label, architecture, load_s = load_transformers_classifier(
                spec.model_id
            )
        except Exception as e:
            err = last_load_error(spec.model_id) or str(e)
            return HFPredictionResult(
                status="model_unavailable",
                crop=crop_name,
                raw_label=None,
                display_label=None,
                confidence=None,
                model_id=spec.model_id,
                architecture=spec.architecture,
                message=f"Failed to load Hugging Face model '{spec.model_id}': {err}",
            )

        try:
            image = bytes_to_rgb_pil(image_bytes)
            inputs = processor(images=image, return_tensors="pt")
            device = next(model.parameters()).device
            inputs = {k: v.to(device=device, dtype=model.dtype) if v.is_floating_point() else v.to(device) for k, v in inputs.items()}

            t0 = time.time()
            with torch.inference_mode():
                logits = model(**inputs).logits[0]
                probs = torch.softmax(logits.float(), dim=-1)
            infer_s = round(time.time() - t0, 4)

            ranked = _rank_predictions(probs, id2label, spec.crop_filter_tokens)
            if not ranked:
                return HFPredictionResult(
                    status="model_unavailable",
                    crop=crop_name,
                    raw_label=None,
                    display_label=None,
                    confidence=None,
                    model_id=spec.model_id,
                    architecture=architecture,
                    message=(
                        f"Model '{spec.model_id}' loaded but no label matched crop "
                        f"'{crop_name}' among its classes."
                    ),
                    id2label=id2label,
                    load_seconds=load_s,
                    infer_seconds=infer_s,
                )

            raw_label, confidence = ranked[0]
            # Skip Invalid if a better crop-matched alternative exists
            if raw_label.lower() == "invalid" and len(ranked) > 1:
                raw_label, confidence = ranked[1]

            alts = [
                {"raw_label": lab, "display_label": _display_from_raw(lab), "confidence": round(sc, 6)}
                for lab, sc in ranked[1:4]
            ]

            return HFPredictionResult(
                status="success",
                crop=crop_name,
                raw_label=raw_label,
                display_label=_display_from_raw(raw_label),
                confidence=round(float(confidence), 6),
                pathogen_type=_guess_pathogen(raw_label),
                model_id=spec.model_id,
                architecture=architecture,
                message=None,
                alternatives=alts,
                id2label=id2label,
                load_seconds=load_s,
                infer_seconds=infer_s,
            )
        except Exception as e:
            logger.exception("HF inference failed for %s", spec.model_id)
            return HFPredictionResult(
                status="model_unavailable",
                crop=crop_name,
                raw_label=None,
                display_label=None,
                confidence=None,
                model_id=spec.model_id,
                architecture=spec.architecture,
                message=f"Inference failed for '{spec.model_id}': {e}",
            )


hf_disease_classifier = HuggingFaceDiseaseClassifier()
