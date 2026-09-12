import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response
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

FALLBACK_PLACEHOLDER_PATH = os.path.join(os.path.dirname(__file__), "assets", "placeholder_leaf.jpg")
FALLBACK_LEAF_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" rx="24" fill="#0f172a"/>
  <circle cx="200" cy="200" r="110" fill="#064e3b"/>
  <circle cx="200" cy="200" r="85" fill="#10b981"/>
  <path d="M200 120 C270 170 280 240 200 290 C120 240 130 170 200 120 Z" fill="#059669"/>
  <path d="M200 130 L200 285" stroke="#d1fae5" stroke-width="4" stroke-linecap="round"/>
  <path d="M200 180 L240 160 M200 180 L160 160 M200 220 L250 200 M200 220 L150 200" stroke="#d1fae5" stroke-width="2" stroke-linecap="round"/>
  <text x="200" y="340" font-family="system-ui, sans-serif" font-size="14" font-weight="600" fill="#94a3b8" text-anchor="middle">CropShield AI Scan</text>
</svg>"""


@app.get("/uploads/{file_path:path}")
async def serve_upload(file_path: str):
    """Serve uploaded user images from disk, or return a clean placeholder if disk is wiped on container redeploy."""
    safe_name = os.path.basename(file_path)
    disk_path = os.path.join(settings.UPLOAD_DIR, safe_name)
    if os.path.isfile(disk_path):
        return FileResponse(disk_path)

    if os.path.isfile(FALLBACK_PLACEHOLDER_PATH):
        return FileResponse(
            FALLBACK_PLACEHOLDER_PATH,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=86400",
                "X-CropShield-Fallback": "true",
            },
        )
    return Response(
        content=FALLBACK_LEAF_SVG,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-CropShield-Fallback": "true",
        },
    )

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


@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/health", methods=["GET", "HEAD"])
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": None if _IS_PROD else "/docs",
        "api_v1": settings.API_V1_STR,
        "disease_inference": _disease_inference_label(),
        "pest_inference": "HUGGINGFACE_YOLO" if settings.USE_PEST_HF_MODEL else "OPERATIONAL",
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.ENVIRONMENT != "production")
