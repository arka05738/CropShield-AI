"""Internal pest detection schemas (object detection)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class PestModelSpec:
    """Registered pest detector identity."""

    key: str
    model_id: str
    architecture: str
    provider: str
    task: str = "object-detection"
    class_count: Optional[int] = None
    note: str = ""


@dataclass
class PestBBox:
    """Pixel-space axis-aligned bounding box from the detector."""

    x1: float
    y1: float
    x2: float
    y2: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "x1": round(self.x1, 2),
            "y1": round(self.y1, 2),
            "x2": round(self.x2, 2),
            "y2": round(self.y2, 2),
        }

    @property
    def area(self) -> float:
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)


@dataclass
class PestObjectDetection:
    """One detected pest instance — exact model label preserved as raw_label."""

    pest: str
    raw_label: str
    confidence: float
    bbox: PestBBox
    class_id: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pest": self.pest,
            "raw_label": self.raw_label,
            "confidence": round(float(self.confidence), 6),
            "bbox": self.bbox.to_dict(),
            "class_id": self.class_id,
        }


@dataclass
class PestDetectionResult:
    """Full detector output for one image."""

    detections: List[PestObjectDetection] = field(default_factory=list)
    count: int = 0
    image_width: int = 0
    image_height: int = 0
    model_id: str = ""
    model_provider: str = "huggingface"
    architecture: str = ""
    inference_mode: str = "unavailable"
    confidence_threshold: float = 0.25
    load_seconds: Optional[float] = None
    inference_ms: Optional[float] = None
    severity: str = "none"
    severity_note: str = (
        "AI-estimated preliminary severity — not an agronomic diagnosis."
    )
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detections": [d.to_dict() for d in self.detections],
            "count": self.count,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "model_id": self.model_id,
            "model_provider": self.model_provider,
            "architecture": self.architecture,
            "inference_mode": self.inference_mode,
            "confidence_threshold": self.confidence_threshold,
            "load_seconds": self.load_seconds,
            "inference_ms": self.inference_ms,
            "severity": self.severity,
            "severity_note": self.severity_note,
            "error": self.error,
        }
