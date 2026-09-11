"""
Internal prediction types for Hugging Face disease inference.
Separate from API Pydantic schemas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HFModelSpec:
    """Verified crop → Hugging Face model routing entry."""

    key: str
    model_id: str
    framework: str  # transformers
    architecture: str
    # Lowercase substrings that must appear in multi-crop model labels.
    # Empty list = single-crop specialist: all model classes belong to this crop.
    crop_filter_tokens: List[str]
    notes: str = ""


@dataclass
class HFPredictionResult:
    status: str  # success | model_unavailable | error
    crop: str
    raw_label: Optional[str] = None
    display_label: Optional[str] = None
    confidence: Optional[float] = None
    pathogen_type: str = "Unknown"
    model_id: Optional[str] = None
    architecture: Optional[str] = None
    provider: str = "huggingface"
    message: Optional[str] = None
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    id2label: Dict[str, str] = field(default_factory=dict)
    load_seconds: Optional[float] = None
    infer_seconds: Optional[float] = None
