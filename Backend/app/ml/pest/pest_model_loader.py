"""Lazy-loading / caching for the primary Ultralytics pest detector."""
from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings
from app.ml.pest.pest_registry import primary_pest_spec

logger = logging.getLogger("cropshield.ml.pest_loader")

# model_id → (yolo_model, names_dict, architecture, load_seconds)
_CACHE: Dict[str, Tuple[Any, Dict[int, str], str, float]] = {}
_LOCK = threading.Lock()
_ERRORS: Dict[str, str] = {}
_LAST_LOAD_SECONDS: Dict[str, float] = {}


def get_cached_pest_model(model_id: str) -> Optional[Tuple[Any, Dict[int, str], str, float]]:
    return _CACHE.get(model_id)


def last_pest_load_error(model_id: str) -> Optional[str]:
    return _ERRORS.get(model_id)


def last_pest_load_seconds(model_id: str) -> Optional[float]:
    return _LAST_LOAD_SECONDS.get(model_id)


def load_pest_yolo(model_id: Optional[str] = None) -> Tuple[Any, Dict[int, str], str, float]:
    """
    Download (if needed) and load Ultralytics YOLO weights once per model_id.
    Thread-safe. Uses HF Hub when model_id is a repo id; local path also supported.
    """
    spec = primary_pest_spec()
    mid = (model_id or spec.model_id).strip()
    if not mid:
        raise RuntimeError("PEST_HF_MODEL_ID is empty")

    cached = _CACHE.get(mid)
    if cached is not None:
        return cached

    with _LOCK:
        cached = _CACHE.get(mid)
        if cached is not None:
            return cached

        try:
            from ultralytics import YOLO
            from huggingface_hub import hf_hub_download

            t0 = time.time()
            logger.info("Loading pest YOLO model: %s", mid)

            # Local filesystem path override
            local_path = (settings.PEST_MODEL_PATH or "").strip()
            if local_path:
                weights = local_path
            elif mid.endswith(".pt") or "/" not in mid or mid.startswith(".") or mid.startswith("/"):
                weights = mid
            else:
                token = (settings.HF_TOKEN or "").strip() or None
                weights = hf_hub_download(
                    repo_id=mid,
                    filename="best.pt",
                    token=token,
                )

            model = YOLO(weights)
            names_raw = model.names
            if isinstance(names_raw, dict):
                names = {int(k): str(v) for k, v in names_raw.items()}
            else:
                names = {i: str(n) for i, n in enumerate(names_raw)}

            load_seconds = round(time.time() - t0, 3)
            arch = spec.architecture
            entry = (model, names, arch, load_seconds)
            _CACHE[mid] = entry
            _LAST_LOAD_SECONDS[mid] = load_seconds
            _ERRORS.pop(mid, None)
            logger.info(
                "Pest YOLO ready id=%s classes=%s load_s=%s",
                mid,
                len(names),
                load_seconds,
            )
            return entry
        except Exception as e:
            _ERRORS[mid] = f"{type(e).__name__}: {e}"
            logger.error("Failed to load pest model %s: %s", mid, e)
            raise
