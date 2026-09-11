"""
Primary pest object detector (YOLO11s / IP102).

Returns bounding boxes from Ultralytics — never invents pests when empty.
"""
from __future__ import annotations

import logging
import tempfile
import time
from pathlib import Path
from typing import List, Optional

from app.core.config import settings
from app.ml.pest.pest_model_loader import last_pest_load_seconds, load_pest_yolo
from app.ml.pest.pest_registry import primary_pest_spec
from app.ml.pest.pest_schema import PestBBox, PestDetectionResult, PestObjectDetection
from app.ml.pest.preprocessing import bytes_to_rgb_pil

logger = logging.getLogger("cropshield.ml.pest_detector")


def estimate_preliminary_severity(
    detections: List[PestObjectDetection],
    image_width: int,
    image_height: int,
) -> str:
    """
    Transparent heuristic only — not agronomic damage %.

    Uses detection count, max confidence, and approximate image-space box density.
    """
    if not detections:
        return "none"
    img_area = max(1.0, float(image_width * image_height))
    total_box_area = sum(d.bbox.area for d in detections)
    density = total_box_area / img_area
    max_conf = max(d.confidence for d in detections)
    count = len(detections)

    # Documented rules (preliminary AI estimate):
    # high: many boxes OR high density OR very high confidence with multiple
    if count >= 5 or density >= 0.12 or (count >= 3 and max_conf >= 0.70):
        return "high"
    if count >= 2 or density >= 0.04 or max_conf >= 0.55:
        return "moderate"
    return "low"


class PestObjectDetector:
    """Lazy-cached primary HF pest YOLO detector."""

    def __init__(self) -> None:
        self.spec = primary_pest_spec()

    @property
    def model_id(self) -> str:
        return self.spec.model_id

    @property
    def threshold(self) -> float:
        return float(settings.PEST_CONFIDENCE_THRESHOLD)

    @property
    def enabled(self) -> bool:
        return bool(settings.USE_PEST_HF_MODEL) and not settings.USE_MOCK_PEST

    def detect(self, image_bytes: bytes, crop_hint: Optional[str] = None) -> PestDetectionResult:
        """
        Run object detection. crop_hint is metadata only (model is not crop-gated).
        """
        _ = crop_hint  # reserved for future crop-conditioned post-filters
        spec = primary_pest_spec()
        conf_th = self.threshold

        try:
            image = bytes_to_rgb_pil(image_bytes)
        except Exception as e:
            return PestDetectionResult(
                inference_mode="unavailable",
                model_id=spec.model_id,
                error=f"Invalid image: {e}",
                confidence_threshold=conf_th,
            )

        w, h = int(image.width), int(image.height)

        if settings.USE_MOCK_PEST:
            return PestDetectionResult(
                detections=[],
                count=0,
                image_width=w,
                image_height=h,
                model_id=spec.model_id,
                inference_mode="mock_disabled_for_od_endpoint",
                confidence_threshold=conf_th,
                severity="none",
                error=(
                    "USE_MOCK_PEST=true is not used by the real pest OD endpoint. "
                    "Set USE_MOCK_PEST=false and USE_PEST_HF_MODEL=true."
                ),
            )

        if not settings.USE_PEST_HF_MODEL:
            return PestDetectionResult(
                detections=[],
                count=0,
                image_width=w,
                image_height=h,
                model_id=spec.model_id,
                inference_mode="unavailable",
                confidence_threshold=conf_th,
                severity="none",
                error="USE_PEST_HF_MODEL=false",
            )

        try:
            model, names, arch, load_s = load_pest_yolo(spec.model_id)
        except Exception as e:
            return PestDetectionResult(
                detections=[],
                count=0,
                image_width=w,
                image_height=h,
                model_id=spec.model_id,
                architecture=spec.architecture,
                inference_mode="unavailable",
                confidence_threshold=conf_th,
                severity="none",
                error=f"{type(e).__name__}: {e}",
            )

        # Ultralytics prefers a path; write a temp JPEG for predict
        tmp_path: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp_path = Path(tmp.name)
                image.save(tmp_path, format="JPEG", quality=92)

            t1 = time.perf_counter()
            results = model.predict(
                source=str(tmp_path),
                imgsz=640,
                conf=conf_th,
                verbose=False,
                device="cpu",
            )
            inference_ms = round((time.perf_counter() - t1) * 1000, 1)
        finally:
            if tmp_path is not None:
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:
                    pass

        detections: List[PestObjectDetection] = []
        r0 = results[0] if results else None
        if r0 is not None and r0.boxes is not None and len(r0.boxes):
            for box in r0.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                if conf < conf_th:
                    continue
                xyxy = box.xyxy[0].tolist()
                raw = names.get(cls_id, str(cls_id))
                # Preserve exact model label — do not rename
                detections.append(
                    PestObjectDetection(
                        pest=raw,
                        raw_label=raw,
                        confidence=conf,
                        bbox=PestBBox(
                            x1=float(xyxy[0]),
                            y1=float(xyxy[1]),
                            x2=float(xyxy[2]),
                            y2=float(xyxy[3]),
                        ),
                        class_id=cls_id,
                    )
                )

        severity = estimate_preliminary_severity(detections, w, h)
        load_seconds = last_pest_load_seconds(spec.model_id) or load_s

        logger.info(
            "Pest OD done model=%s count=%s severity=%s infer_ms=%s crop_hint=%s",
            spec.model_id,
            len(detections),
            severity,
            inference_ms,
            crop_hint,
        )

        return PestDetectionResult(
            detections=detections,
            count=len(detections),
            image_width=w,
            image_height=h,
            model_id=spec.model_id,
            model_provider="huggingface",
            architecture=arch,
            inference_mode="huggingface_yolo",
            confidence_threshold=conf_th,
            load_seconds=load_seconds,
            inference_ms=inference_ms,
            severity=severity,
            severity_note=(
                "AI-estimated preliminary severity — not an agronomic diagnosis."
            ),
        )


pest_object_detector = PestObjectDetector()
