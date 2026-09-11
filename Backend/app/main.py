import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.startup_checks import validate_runtime_settings
from app.core.database import connect_to_mongo, close_mongo_connection, persistence_mode
from app.services.seed_data import seed_initial_data
from app.api.router import api_router
from app.api.v1.health import _disease_inference_label

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("cropshield")

_IS_PROD = settings.ENVIRONMENT.lower().strip() == "production"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Initializing CropShield AI backend (environment=%s)...",
        settings.ENVIRONMENT,
    )
    # Fail closed on unsafe production configuration before serving traffic
    validate_runtime_settings(settings)

    await connect_to_mongo()
    logger.info("Persistence mode: %s", persistence_mode())

    await seed_initial_data()
    logger.info("CropShield AI startup completed successfully.")
    yield
    logger.info("Shutting down CropShield AI backend...")
    await close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "CropShield AI API for SIH 2026 (PS 26131). "
        "Disease inference uses verified Hugging Face multi-model routing when enabled. "
        "Pest detection is UNAVAILABLE by default (no YOLO weights shipped). "
        "Recommendations are grounded in curated knowledge or return guidance-unavailable."
    ),
    lifespan=lifespan,
    docs_url=None if _IS_PROD else "/docs",
    redoc_url=None if _IS_PROD else "/redoc",
)

# Bearer-token API — credentials flag not required for Authorization headers.
# Origins come only from CORS_ORIGINS (never '*').
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Do not leak stack traces, paths, or env material to clients."""
    logger.exception("Unhandled server error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


@app.get("/")
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": None if _IS_PROD else "/docs",
        "api_v1": settings.API_V1_STR,
        "disease_inference": _disease_inference_label(),
        "pest_inference": "UNAVAILABLE_BY_DEFAULT",
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.ENVIRONMENT != "production")
