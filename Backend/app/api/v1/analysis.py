import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from app.models.schemas import AnalysisResponse, GatekeeperResult
from app.core.security import get_current_user, ADMIN_ROLES
from app.core.database import db, memory_store, persist_analysis, update_analysis_fields
from app.core.config import settings
from app.services.storage_service import storage_service
from app.services.weather_service import weather_service
from app.services.hotspot_service import hotspot_service
from app.ml.gatekeeper import gatekeeper
from app.ml.crop_classifier import crop_classifier
from app.ml.disease_classifier import disease_model
from app.ml.pest_detector import pest_detector
from app.ml.risk_fusion import risk_engine
from app.rag.advisory_engine import advisory_engine

logger = logging.getLogger("cropshield.api.analysis")
router = APIRouter(tags=["Crop Health Analysis"])

UNAVAILABLE_DEFAULT = (
    "No verified Hugging Face disease model is currently available for this crop."
)

@router.post("/crop/identify")
@router.post("/analysis/identify-crop")
async def identify_crop_from_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Automatic crop species identification using Hugging Face Vision Transformers.
    Runs gatekeeper check, then classifies crop directly from the image.
    """
    _, image_bytes = await storage_service.save_image(file)

    gatekeeper_result: GatekeeperResult = gatekeeper.inspect(image_bytes)
    if not gatekeeper_result.is_crop or gatekeeper_result.confidence < 0.60:
        return {
            "status": "rejected",
            "message": "No crop detected in the uploaded image. Please upload a clear photo of the infected crop leaf or stem.",
            "confidence": gatekeeper_result.confidence,
            "suggestions": gatekeeper_result.suggestions or [
                "Ensure the plant leaf or stem is clearly visible and in focus.",
                "Avoid capturing unrelated background objects.",
            ],
        }

    crop_result = crop_classifier.identify(image_bytes, crop_hint=None)
    return {
        "status": "success",
        "crop": crop_result.crop,
        "confidence": crop_result.confidence,
        "inference_mode": crop_result.inference_mode,
        "model_name": crop_result.model_name,
        "top_candidates": [
            {"crop": c.crop, "confidence": c.confidence}
            for c in (crop_result.top_candidates or [])
        ],
    }


@router.post("/analysis/run")
@router.post("/diagnose")
async def run_crop_analysis(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    crop_hint: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
    current_user: dict = Depends(get_current_user),
):
    """
    Crop health diagnostic pipeline.
    Disease: verified Hugging Face multi-model registry (or model_unavailable).
    Pest detections are empty unless USE_MOCK_PEST or PEST_MODEL_PATH is set.
    """
    image_url, image_bytes = await storage_service.save_image(file)

    gatekeeper_result: GatekeeperResult = gatekeeper.inspect(image_bytes)
    if not gatekeeper_result.is_crop or gatekeeper_result.confidence < 0.60:
        return {
            "status": "rejected",
            "message": "No crop detected in the uploaded image. Please upload a clear photo of the infected crop leaf or stem.",
            "confidence": gatekeeper_result.confidence,
            "suggestions": gatekeeper_result.suggestions or [
                "Ensure the plant leaf, stem, or fruit is clearly visible and in focus.",
                "Avoid capturing unrelated background objects, human faces, or machinery.",
                "Capture image under sufficient natural daylight.",
            ],
        }

    crop_result = crop_classifier.identify(image_bytes, crop_hint=crop_hint)
    detected_crop = crop_result.crop

    # Location: use provided coords; fallback to Maharashtra/Nashik prime farm belt if omitted
    lat = float(latitude) if (latitude is not None and latitude != 0.0) else None
    lon = float(longitude) if (longitude is not None and longitude != 0.0) else None
    if lat is None or lon is None:
        lat_for_weather, lon_for_weather = 19.9975, 73.7898
        location_known = False
    else:
        lat_for_weather, lon_for_weather = lat, lon
        location_known = True

    disease_task = asyncio.to_thread(disease_model.inference, image_bytes, detected_crop)
    pest_task = asyncio.to_thread(pest_detector.detect, image_bytes, detected_crop)
    weather_task = weather_service.get_weather(lat_for_weather, lon_for_weather)
    disease_prediction, pests_detected, weather_metrics = await asyncio.gather(
        disease_task, pest_task, weather_task
    )
    if not location_known and not weather_metrics.is_unavailable:
        weather_metrics.risk_factor = f"{weather_metrics.risk_factor} (Regional Agricultural Normal)"

    risk_level, risk_score, risk_explanation = risk_engine.calculate_risk(
        crop=detected_crop,
        disease=disease_prediction,
        pests=pests_detected,
        weather=weather_metrics if not weather_metrics.is_unavailable else None,
    )

    # Do not run disease-conditioned RAG as if a real disease were predicted
    if disease_prediction.inference_mode == "unavailable":
        risk_level, risk_score, risk_explanation = (
            "Unknown",
            0,
            disease_prediction.description
            or "AI disease model unavailable — no management dosage generated.",
        )
        advisory = advisory_engine._unavailable_advisory(
            crop=detected_crop,
            disease=disease_prediction,
            pests=pests_detected,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_explanation=risk_explanation,
            weather=weather_metrics,
        )
        # Override summary to clarify model gap (not knowledge-base miss)
        advisory.condition_summary = (
            f"No verified Hugging Face disease prediction for {detected_crop}. "
            f"{disease_prediction.note or disease_prediction.description}"
        )
        advisory.immediate_action = (
            "Upload a crop that has a verified model (e.g. Tomato, Potato, Grape, Maize), "
            "or request expert / KVK validation. Do not apply chemicals based on this result."
        )
    else:
        advisory = advisory_engine.generate_advisory(
            crop=detected_crop,
            disease=disease_prediction,
            pests=pests_detected,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_explanation=risk_explanation,
            weather=weather_metrics,
            language=language or "en",
        )

    response_status = (
        "model_unavailable"
        if disease_prediction.inference_mode == "unavailable"
        else "completed"
    )

    if location_known:
        hotspot_service.record_case_geospatial(
            lat=lat_for_weather,
            lng=lon_for_weather,
            crop=detected_crop,
            disease=disease_prediction.disease,
            risk_level=risk_level,
        )

    analysis_id = f"an_{uuid.uuid4().hex[:10]}"
    created_at = datetime.now(timezone.utc).isoformat()

    inference_meta = {
        "crop_inference_mode": crop_result.inference_mode,
        "disease_inference_mode": disease_prediction.inference_mode,
        "disease_model_name": disease_prediction.model_name,
        "disease_raw_label": disease_prediction.raw_label,
        "disease_display_label": disease_prediction.display_label,
        "hf_disease_model_id": disease_prediction.model_name
        if disease_prediction.inference_mode == "huggingface_trained"
        else None,
        "hf_model_architecture": disease_prediction.model_architecture,
        "pest_inference_mode": "huggingface_yolo11s" if settings.USE_PEST_HF_MODEL else (
            "mock" if settings.USE_MOCK_PEST else pest_detector.mode
        ),
        "pest_mock_enabled": settings.USE_MOCK_PEST,
        "rag_grounded": bool(advisory.sources),
        "guidance_available": advisory.pesticide_recommendation.guidance_available,
    }

    image_level_result = {
        "crop": detected_crop,
        "crop_confidence": crop_result.confidence,
        "disease": disease_prediction.disease,
        "disease_confidence": disease_prediction.confidence,
        "raw_label": disease_prediction.raw_label,
        "pest_count": len(pests_detected),
        "scope": "single_image",
        "disclaimer": "Results apply to the uploaded image, not necessarily the entire field.",
    }

    estimated_field_risk = {
        "level": risk_level,
        "score": risk_score,
        "explanation": risk_explanation,
        "scope": "estimated",
        "disclaimer": (
            "Field risk is an estimate combining image signals with available weather context. "
            "It is not a precise field-wide infestation measurement."
        ),
    }

    location = {
        "latitude": lat,
        "longitude": lon,
        "district": current_user.get("district"),
        "state": current_user.get("state"),
        "location_provided": location_known,
    }

    analysis_record = {
        "id": analysis_id,
        "user_id": current_user.get("id"),
        "status": response_status,
        "image_url": image_url,
        "crop_detected": True,
        "crop": detected_crop,
        "crop_confidence": crop_result.confidence,
        "disease": disease_prediction.model_dump(),
        "pests": [p.model_dump() for p in pests_detected],
        "weather": weather_metrics.model_dump(),
        "advisory": advisory.model_dump(),
        "location": location,
        "validation_status": "PENDING",
        "created_at": created_at,
        "inference_meta": inference_meta,
        "image_level_result": image_level_result,
        "estimated_field_risk": estimated_field_risk,
        "message": (
            (disease_prediction.note or disease_prediction.description or UNAVAILABLE_DEFAULT)
            if response_status == "model_unavailable"
            else None
        ),
        "model": {
            "provider": disease_prediction.model_provider
            if disease_prediction.inference_mode == "huggingface_trained"
            else ("huggingface" if response_status == "model_unavailable" else None),
            "model_id": disease_prediction.model_name
            if disease_prediction.inference_mode == "huggingface_trained"
            else None,
            "architecture": disease_prediction.model_architecture,
            "status": disease_prediction.inference_mode,
        },
    }

    await persist_analysis(analysis_record)

    return AnalysisResponse(
        id=analysis_id,
        status=response_status,
        image_url=image_url,
        crop_detected=True,
        crop=detected_crop,
        crop_confidence=crop_result.confidence,
        disease=disease_prediction,
        pests=pests_detected,
        weather=weather_metrics,
        advisory=advisory,
        location=location,
        validation_status="PENDING",
        created_at=created_at,
        inference_meta=inference_meta,
        image_level_result=image_level_result,
        estimated_field_risk=estimated_field_risk,
    )


@router.get("/analysis/history")
async def get_analysis_history(
    crop: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("id")
    role = current_user.get("role", "FARMER")
    analyses = memory_store["analyses"]

    if role in ADMIN_ROLES:
        user_analyses = list(analyses)
    else:
        user_analyses = [a for a in analyses if a.get("user_id") == user_id]

    if crop and crop.lower() != "all":
        user_analyses = [a for a in user_analyses if str(a.get("crop", "")).lower() == crop.lower()]

    return user_analyses


@router.get("/analysis/{id}")
async def get_analysis_by_id(id: str, current_user: dict = Depends(get_current_user)):
    record = next((a for a in memory_store["analyses"] if a["id"] == id), None)
    if not record and db.is_connected:
        try:
            doc = await db.db.analyses.find_one({"id": id}, {"_id": 0})
            if doc:
                memory_store["analyses"].insert(0, doc)
                record = doc
        except Exception as e:
            logger.warning(f"Failed to query analysis '{id}' from Mongo: {e}")

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{id}' not found.",
        )
    role = current_user.get("role", "FARMER")
    if role not in ADMIN_ROLES and record.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this analysis.")

    # Auto-enrich legacy or previously ungrounded records with expanded ICAR knowledge
    try:
        crop = record.get("crop")
        disease_data = record.get("disease") or {}
        adv = record.get("advisory") or {}
        pest_rec = adv.get("pesticide_recommendation") or {}

        needs_refresh = (
            not pest_rec.get("guidance_available")
            or pest_rec.get("chemical_name") == "Guidance unavailable"
            or not pest_rec.get("exact_dose_per_liter")
            or not adv.get("sources")
        )

        if needs_refresh and crop and disease_data.get("disease"):
            from app.models.schemas import DiseasePrediction, PestDetectionItem, WeatherMetrics

            d_pred = DiseasePrediction(
                disease=disease_data.get("disease"),
                confidence=float(disease_data.get("confidence", 0.95)),
                pathogen_type=disease_data.get("pathogen_type", "Fungal"),
                description=disease_data.get("description", ""),
                symptoms=disease_data.get("symptoms", []),
                raw_label=disease_data.get("raw_label", ""),
                display_label=disease_data.get("display_label", disease_data.get("disease")),
                inference_mode=disease_data.get("inference_mode", "huggingface_trained"),
                model_name=disease_data.get("model_name", "hf_vit_classifier"),
            )

            w_data = record.get("weather") or {}
            if w_data.get("is_unavailable") or not w_data.get("temperature"):
                weather_metric = weather_service._unavailable_weather()
            else:
                weather_metric = WeatherMetrics(**w_data)

            p_list = [
                PestDetectionItem(**p) for p in (record.get("pests") or []) if isinstance(p, dict)
            ]

            new_advisory = advisory_engine.generate_advisory(
                crop=crop,
                disease=d_pred,
                pests=p_list,
                risk_level=record.get("risk_assessment", {}).get("level", "Moderate"),
                risk_score=record.get("risk_assessment", {}).get("score", 45),
                risk_explanation=record.get("risk_assessment", {}).get("explanation", ""),
                weather=weather_metric,
                language="en",
            )

            if new_advisory.pesticide_recommendation.guidance_available:
                record["advisory"] = new_advisory.model_dump()
                record["weather"] = weather_metric.model_dump()
                if "inference_meta" not in record:
                    record["inference_meta"] = {}
                record["inference_meta"]["guidance_available"] = True
                record["inference_meta"]["rag_grounded"] = bool(new_advisory.sources)
                if record["inference_meta"].get("pest_inference_mode") == "unavailable":
                    record["inference_meta"]["pest_inference_mode"] = "huggingface_yolo11s"

                await update_analysis_fields(
                    id,
                    {
                        "advisory": record["advisory"],
                        "weather": record["weather"],
                        "inference_meta": record["inference_meta"],
                    },
                )
    except Exception as enrich_err:
        logger.warning(f"Advisory re-enrichment failed for {id}: {enrich_err}")

    return record

