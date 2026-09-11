"""
Dedicated pest object-detection API.

Separate from POST /diagnose (disease pipeline). Does not modify disease history.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.database import memory_store, persist_pest_analysis
from app.core.security import get_current_user, ADMIN_ROLES
from app.ml.pest import pest_object_detector
from app.models.schemas import (
    PestAdvisoryBrief,
    PestDetectResponse,
    PestModelMeta,
    PestObjectDetectionItem,
    PestPixelBBox,
)
from app.rag.pest_advisory import generate_pest_advisory
from app.services.storage_service import storage_service

logger = logging.getLogger("cropshield.api.pests")

router = APIRouter(prefix="/pests", tags=["Pest Detection"])


@router.post("/detect", response_model=PestDetectResponse)
async def detect_pests(
    file: UploadFile = File(...),
    crop_hint: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Real YOLO pest object detection (primary HF model).
    Returns bounding boxes; empty detections → status=no_pest_detected (not 'pest-free').
    """
    image_url, image_bytes = await storage_service.save_image(file)

    result = await asyncio.to_thread(
        pest_object_detector.detect,
        image_bytes,
        crop_hint,
    )

    if result.error and result.inference_mode == "unavailable":
        # Still persist a transparent failure record? Prefer HTTP 503 for hard load failure.
        if "Invalid image" in (result.error or ""):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Pest detector unavailable: {result.error}",
        )

    detections: List[PestObjectDetectionItem] = [
        PestObjectDetectionItem(
            pest=d.pest,
            raw_label=d.raw_label,
            confidence=round(float(d.confidence), 6),
            bbox=PestPixelBBox(**d.bbox.to_dict()),
            class_id=d.class_id,
        )
        for d in result.detections
    ]
    count = len(detections)
    api_status = "pests_detected" if count > 0 else "no_pest_detected"

    labels = [d.raw_label for d in result.detections]
    advisory: PestAdvisoryBrief = generate_pest_advisory(
        pest_labels=labels,
        crop_hint=crop_hint,
        count=count,
        severity=result.severity,
    )

    analysis_id = f"pest_{uuid.uuid4().hex[:10]}"
    created_at = datetime.now(timezone.utc).isoformat()
    primary_pest = labels[0] if labels else None
    primary_conf = detections[0].confidence if detections else None
    primary_bbox = detections[0].bbox.model_dump() if detections else None

    model_meta = PestModelMeta(
        provider=result.model_provider or "huggingface",
        model_id=result.model_id,
        architecture=result.architecture,
        inference_mode=result.inference_mode,
        confidence_threshold=result.confidence_threshold,
        load_seconds=result.load_seconds,
        inference_ms=result.inference_ms,
    )

    record = {
        "id": analysis_id,
        "record_type": "pest",
        "user_id": current_user["id"],
        "status": api_status,
        "image_url": image_url,
        "crop": crop_hint,
        "crop_hint": crop_hint,
        "pest": primary_pest,
        "raw_label": primary_pest,
        "confidence": primary_conf,
        "bbox": primary_bbox,
        "detections": [d.model_dump() for d in detections],
        "count": count,
        "image_width": result.image_width,
        "image_height": result.image_height,
        "severity": result.severity,
        "severity_label": result.severity_note,
        "model": model_meta.model_dump(),
        "model_provider": model_meta.provider,
        "model_id": model_meta.model_id,
        "advisory": advisory.model_dump(),
        "guidance_available": advisory.guidance_available,
        "created_at": created_at,
        "inference_meta": {
            "pest_inference_mode": result.inference_mode,
            "confidence_threshold": result.confidence_threshold,
            "load_seconds": result.load_seconds,
            "inference_ms": result.inference_ms,
            "rag_grounded": advisory.guidance_available,
            "guidance_available": advisory.guidance_available,
            "threshold_is_not_accuracy": True,
            "author_reported_val_map_note": (
                "Model card val mAP@0.5=0.815 is NOT CropShield accuracy."
            ),
        },
    }
    await persist_pest_analysis(record)

    return PestDetectResponse(
        id=analysis_id,
        status=api_status,
        image_url=image_url,
        crop_hint=crop_hint,
        detections=detections,
        count=count,
        image_width=result.image_width,
        image_height=result.image_height,
        severity=result.severity,
        severity_label=result.severity_note,
        model=model_meta,
        advisory=advisory,
        created_at=created_at,
        inference_meta=record["inference_meta"],
    )


@router.get("/history")
async def pest_history(current_user: dict = Depends(get_current_user)):
    """Farmer-owned pest detection history (separate from disease analyses)."""
    uid = current_user["id"]
    rows = [
        a for a in memory_store.get("pest_analyses", [])
        if a.get("user_id") == uid
    ]
    return {"items": rows, "count": len(rows), "record_type": "pest"}


@router.get("/{pest_id}")
async def get_pest_analysis(pest_id: str, current_user: dict = Depends(get_current_user)):
    row = next(
        (a for a in memory_store.get("pest_analyses", []) if a.get("id") == pest_id),
        None,
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pest analysis not found.")
    if row.get("user_id") != current_user["id"] and current_user.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
    return row
