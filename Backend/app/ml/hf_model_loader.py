"""
Lazy-loading / caching Hugging Face image-classification models.

Public Hub models — HF_TOKEN optional (rate limits only).
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings

logger = logging.getLogger("cropshield.ml.hf_loader")

# model_id → (processor, model, id2label, architecture, load_seconds)
_CACHE: Dict[str, Tuple[Any, Any, Dict[str, str], str, float]] = {}
_LOCK = threading.Lock()
_ERRORS: Dict[str, str] = {}


def get_cached_model(model_id: str) -> Optional[Tuple[Any, Any, Dict[str, str], str, float]]:
    return _CACHE.get(model_id)


def last_load_error(model_id: str) -> Optional[str]:
    return _ERRORS.get(model_id)


def load_transformers_classifier(model_id: str) -> Tuple[Any, Any, Dict[str, str], str, float]:
    """
    Load AutoImageProcessor + AutoModelForImageClassification once per model_id.
    Thread-safe. Raises on failure (caller maps to model_unavailable).
    """
    cached = _CACHE.get(model_id)
    if cached is not None:
        return cached

    with _LOCK:
        cached = _CACHE.get(model_id)
        if cached is not None:
            return cached

        try:
            import gc
            import torch
            from transformers import AutoConfig, AutoImageProcessor, AutoModelForImageClassification

            # Evict existing model from cache to stay strictly within 512MB RAM on Render
            while _CACHE:
                old_k, old_v = _CACHE.popitem()
                try:
                    del old_v
                except Exception:
                    pass
            gc.collect()

            token = (settings.HF_TOKEN or "").strip() or None
            kwargs: Dict[str, Any] = {}
            if token:
                kwargs["token"] = token

            t0 = time.time()
            logger.info("Loading Hugging Face model: %s", model_id)
            cfg = AutoConfig.from_pretrained(model_id, **kwargs)
            architecture = (cfg.architectures or [getattr(cfg, "model_type", "unknown")])[0]
            id2label = {str(k): str(v) for k, v in dict(getattr(cfg, "id2label", {}) or {}).items()}

            processor = AutoImageProcessor.from_pretrained(model_id, **kwargs)
            model = AutoModelForImageClassification.from_pretrained(model_id, **kwargs)
            model.eval()
            load_seconds = round(time.time() - t0, 3)

            # Force CPU for Render-friendly default; use CUDA if present
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model.to(device)

            entry = (processor, model, id2label, str(architecture), load_seconds)
            _CACHE[model_id] = entry
            _ERRORS.pop(model_id, None)
            logger.info(
                "HF model ready id=%s arch=%s classes=%s load_s=%s device=%s",
                model_id,
                architecture,
                len(id2label),
                load_seconds,
                device,
            )
            return entry
        except Exception as e:
            _ERRORS[model_id] = str(e)
            logger.exception("Failed to load HF model %s", model_id)
            raise


def clear_cache() -> None:
    """Test helper only."""
    with _LOCK:
        _CACHE.clear()
        _ERRORS.clear()
