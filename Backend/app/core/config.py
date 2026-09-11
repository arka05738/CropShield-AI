import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BACKEND_ROOT / ".env")


def parse_cors_origins(value: Optional[str], environment: str) -> List[str]:
    """
    Parse CORS_ORIGINS CSV. Never allow '*'.
    Production + unset → empty (startup validation fails closed).
    Development + unset → localhost Vite defaults.
    """
    env = (environment or "development").lower()
    if not value or not str(value).strip():
        if env == "production":
            return []
        return [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://localhost:3000",
        ]
    origins = [o.strip() for o in str(value).split(",") if o.strip()]
    return [o for o in origins if o != "*"]


class Settings(BaseSettings):
    """
    CORS_ORIGINS is read as a CSV string (not JSON list) via cors_origins_csv,
    then exposed as CORS_ORIGINS list for FastAPI middleware.
    """

    model_config = SettingsConfigDict(case_sensitive=True, extra="allow")

    PROJECT_NAME: str = "CropShield AI"
    VERSION: str = "1.2.0"
    API_V1_STR: str = "/api/v1"

    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALLOW_DEMO_AUTH: bool = False
    ENVIRONMENT: str = "development"
    SEED_DEMO_DATA: bool = False

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    HF_TOKEN: str = ""
    USE_HF_SERVERLESS_API: bool = True
    HF_INFERENCE_ROUTER_URL: str = "https://router.huggingface.co/hf-inference/models"
    USE_HF_DISEASE_MODEL: bool = True
    # Legacy alias — same as HF_MODEL_PLANTVILLAGE
    HF_DISEASE_MODEL_ID: str = "kimcomehome/plantvillage-vit-leaf-disease"
    HF_MODEL_PLANTVILLAGE: str = "kimcomehome/plantvillage-vit-leaf-disease"
    HF_MODEL_SUGARCANE: str = "LishaV01/agriculture-crop-disease-detection"
    HF_MODEL_RICE: str = "wambugu71/crop_leaf_diseases_vit"
    HF_MODEL_WHEAT: str = "wambugu71/crop_leaf_diseases_vit"
    HF_MODEL_COTTON: str = "YaswanthReddy23/ViT_Cotton"
    HF_MODEL_SUNFLOWER: str = "YaswanthReddy23/ViT_Sunflower"

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "cropshield"

    CHROMA_PERSIST_DIR: str = str(BACKEND_ROOT / "data" / "chroma")
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"

    USE_MOCK_AI: bool = False
    USE_MOCK_WEATHER: bool = False
    USE_MOCK_PEST: bool = False
    PEST_MODEL_PATH: str = ""
    # Primary pest OD (Ultralytics YOLO via Hugging Face Hub). Not used when USE_MOCK_PEST=true.
    USE_PEST_HF_MODEL: bool = True
    PEST_HF_MODEL_ID: str = "underdogquality/yolo11s-pest-detection"
    # Ultralytics predict default is 0.25 — detection threshold, NOT accuracy.
    PEST_CONFIDENCE_THRESHOLD: float = 0.25
    DISEASE_MODEL_DIR: str = str(BACKEND_ROOT / "models" / "weights")

    UPLOAD_DIR: str = str(BACKEND_ROOT / "uploads")
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024

    # Comma-separated origins from env CORS_ORIGINS (string, not JSON array)
    cors_origins_csv: Optional[str] = Field(default=None, validation_alias="CORS_ORIGINS")

    def model_post_init(self, __context) -> None:
        # Prefer explicit env if Field missed GROQ_API alias
        if not self.GROQ_API_KEY:
            object.__setattr__(self, "GROQ_API_KEY", os.getenv("GROQ_API") or "")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw = self.cors_origins_csv
        if raw is None:
            raw = os.getenv("CORS_ORIGINS")
        return parse_cors_origins(raw, self.ENVIRONMENT)

    def resolved_jwt_secret(self) -> str:
        secret = (self.JWT_SECRET or "").strip()
        if secret:
            return secret
        if self.ENVIRONMENT.lower() == "production":
            raise RuntimeError(
                "JWT_SECRET must be set in production. "
                "Refusing to use a development fallback secret."
            )
        return "dev-only-cropshield-jwt-change-me"


def _bool_env(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() == "true"


def _build_settings() -> Settings:
    # Normalize bools from env before Settings (pydantic handles most, keep explicit)
    return Settings(
        JWT_SECRET=os.getenv("JWT_SECRET", ""),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7))),
        ALLOW_DEMO_AUTH=_bool_env("ALLOW_DEMO_AUTH", False),
        ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
        SEED_DEMO_DATA=_bool_env("SEED_DEMO_DATA", False),
        GROQ_API_KEY=os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API", ""),
        GROQ_MODEL=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        HF_TOKEN=os.getenv("HF_TOKEN", ""),
        USE_HF_DISEASE_MODEL=_bool_env("USE_HF_DISEASE_MODEL", True),
        HF_DISEASE_MODEL_ID=os.getenv(
            "HF_DISEASE_MODEL_ID",
            os.getenv("HF_MODEL_PLANTVILLAGE", "kimcomehome/plantvillage-vit-leaf-disease"),
        ),
        HF_MODEL_PLANTVILLAGE=os.getenv(
            "HF_MODEL_PLANTVILLAGE",
            os.getenv("HF_DISEASE_MODEL_ID", "kimcomehome/plantvillage-vit-leaf-disease"),
        ),
        HF_MODEL_SUGARCANE=os.getenv(
            "HF_MODEL_SUGARCANE", "LishaV01/agriculture-crop-disease-detection"
        ),
        HF_MODEL_RICE=os.getenv("HF_MODEL_RICE", "wambugu71/crop_leaf_diseases_vit"),
        HF_MODEL_WHEAT=os.getenv("HF_MODEL_WHEAT", "wambugu71/crop_leaf_diseases_vit"),
        HF_MODEL_COTTON=os.getenv("HF_MODEL_COTTON", "YaswanthReddy23/ViT_Cotton"),
        HF_MODEL_SUNFLOWER=os.getenv("HF_MODEL_SUNFLOWER", "YaswanthReddy23/ViT_Sunflower"),
        MONGO_URI=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        MONGO_DB_NAME=os.getenv("MONGO_DB_NAME", "cropshield"),
        CHROMA_PERSIST_DIR=os.getenv("CHROMA_PERSIST_DIR", str(BACKEND_ROOT / "data" / "chroma")),
        OPEN_METEO_URL=os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast"),
        USE_MOCK_AI=_bool_env("USE_MOCK_AI", False),
        USE_MOCK_WEATHER=_bool_env("USE_MOCK_WEATHER", False),
        USE_MOCK_PEST=_bool_env("USE_MOCK_PEST", False),
        PEST_MODEL_PATH=os.getenv("PEST_MODEL_PATH", ""),
        USE_PEST_HF_MODEL=_bool_env("USE_PEST_HF_MODEL", True),
        PEST_HF_MODEL_ID=os.getenv(
            "PEST_HF_MODEL_ID", "underdogquality/yolo11s-pest-detection"
        ),
        PEST_CONFIDENCE_THRESHOLD=float(os.getenv("PEST_CONFIDENCE_THRESHOLD", "0.25")),
        DISEASE_MODEL_DIR=os.getenv("DISEASE_MODEL_DIR", str(BACKEND_ROOT / "models" / "weights")),
        UPLOAD_DIR=os.getenv("UPLOAD_DIR", str(BACKEND_ROOT / "uploads")),
        MAX_UPLOAD_BYTES=int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024))),
        cors_origins_csv=os.getenv("CORS_ORIGINS"),
    )


settings = _build_settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.DISEASE_MODEL_DIR, exist_ok=True)
