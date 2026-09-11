from fastapi import APIRouter
from app.core.config import settings
from app.core.database import db, persistence_mode
from app.rag.chroma_service import chroma_service
from app.ml.pest_detector import pest_detector
from app.ml.pest.pest_registry import primary_pest_spec
from app.ml.hf_crop_registry import build_crop_registry, UNSUPPORTED_CROPS


def _disease_inference_label() -> str:
    if settings.USE_MOCK_AI:
        return "TEST_MOCK"
    if not settings.USE_HF_DISEASE_MODEL:
        return "DISABLED"
    return "HUGGINGFACE_MULTI_MODEL"


def _pest_inference_label() -> str:
    if settings.USE_MOCK_PEST:
        return "MOCK"
    if settings.USE_PEST_HF_MODEL:
        return "HUGGINGFACE_YOLO"
    return pest_detector.mode.upper() if pest_detector.mode != "unavailable" else "UNAVAILABLE"


router = APIRouter(tags=["Health & Status"])


@router.get("/health")
async def health_check():
    """
    Unauthenticated liveness/readiness probe.
    Does not expose secrets, API keys, or JWT material.
    """
    chroma_count = 0
    try:
        if chroma_service.collection:
            chroma_count = chroma_service.collection.count()
    except Exception:
        chroma_count = -1

    routing = {}
    if settings.USE_HF_DISEASE_MODEL and not settings.USE_MOCK_AI:
        routing = {c: s.model_id for c, s in build_crop_registry().items()}

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "persistence_mode": persistence_mode(),
        "mongodb_connected": bool(db.is_connected),
        "chromadb_documents": chroma_count if chroma_count >= 0 else None,
        "chromadb_ok": chroma_count >= 0,
        "llm_configured": bool(settings.GROQ_API_KEY),
        "disease_inference": _disease_inference_label(),
        "hf_models": {
            "plantvillage": settings.HF_MODEL_PLANTVILLAGE,
            "sugarcane": settings.HF_MODEL_SUGARCANE,
            "rice": settings.HF_MODEL_RICE,
            "wheat": settings.HF_MODEL_WHEAT,
            "cotton": settings.HF_MODEL_COTTON,
            "sunflower": settings.HF_MODEL_SUNFLOWER,
        }
        if settings.USE_HF_DISEASE_MODEL
        else None,
        "hf_supported_crops": sorted(set(routing.keys())) if routing else [],
        "hf_unsupported_crops": sorted(UNSUPPORTED_CROPS),
        "pest_inference": _pest_inference_label(),
        "pest_model_id": primary_pest_spec().model_id if settings.USE_PEST_HF_MODEL else None,
        "pest_confidence_threshold": float(settings.PEST_CONFIDENCE_THRESHOLD)
        if settings.USE_PEST_HF_MODEL
        else None,
        "seed_demo_data": bool(settings.SEED_DEMO_DATA) and settings.ENVIRONMENT.lower() != "production",
        "allow_demo_auth": bool(settings.ALLOW_DEMO_AUTH) and settings.ENVIRONMENT.lower() != "production",
    }
