from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Authentication Schemas ---
class UserRole(str):
    FARMER = "FARMER"
    EXTENSION_WORKER = "EXTENSION_WORKER"
    EXPERT = "EXPERT"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "FARMER"
    state: Optional[str] = "Maharashtra"
    district: Optional[str] = "Nashik"
    village: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    created_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Gatekeeper & ML Vision Schemas ---
class GatekeeperResult(BaseModel):
    is_crop: bool
    confidence: float
    message: str
    suggestions: List[str] = []

class CropIdentificationResult(BaseModel):
    crop: str
    confidence: float
    inference_mode: str = "heuristic"  # heuristic | trained | mock
    model_name: Optional[str] = None

class DiseasePrediction(BaseModel):
    disease: Optional[str] = None
    pathogen_type: str = "Unknown"  # Fungal, Bacterial, Viral, Physiological, Healthy, Unknown
    confidence: Optional[float] = None
    description: str = ""
    inference_mode: str = "unavailable"  # huggingface_trained | mock | unavailable
    model_name: Optional[str] = None
    note: Optional[str] = None
    raw_label: Optional[str] = None
    display_label: Optional[str] = None
    model_provider: Optional[str] = None
    model_architecture: Optional[str] = None

class BoundingBox(BaseModel):
    x: float  # Normalized 0.0 - 1.0
    y: float
    width: float
    height: float

class PestDetectionItem(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    confidence: float
    bbox: BoundingBox
    severity: str = "Moderate"  # Low, Moderate, High, Severe
    is_mock: bool = False
    inference_mode: str = "unavailable"  # unavailable | mock | trained
    note: Optional[str] = None

# --- Weather Schemas ---
class WeatherMetrics(BaseModel):
    temperature: float
    relative_humidity: float
    precipitation: float
    wind_speed: float
    cloud_cover: Optional[float] = 0.0
    risk_level: str  # Low, Moderate, High, Critical
    risk_factor: str
    is_cached: bool = False
    is_unavailable: bool = False
    source: str = "open-meteo"  # open-meteo | cache | unavailable | mock

# --- Advisory & IPM Schemas ---
class PesticideRecommendation(BaseModel):
    active_ingredient: str
    chemical_name: str
    exact_dose_per_liter: str
    withholding_period_days: int
    application_method: str
    safety_warnings: List[str]
    guidance_available: bool = True
    unavailable_reason: Optional[str] = None

class FertilizerAdjustment(BaseModel):
    n_ratio: str
    p_ratio: str
    k_ratio: str
    micronutrients: List[str]
    instructions: str

class IPMStrategy(BaseModel):
    cultural: List[str]
    biological: List[str]
    mechanical: List[str]
    chemical: List[str]

class MonitoringPlan(BaseModel):
    day_1: str
    day_3: str
    day_7: str
    day_14: str

class SourceReference(BaseModel):
    title: str
    authority: str
    document_type: str
    page_number: Optional[int] = None
    url: Optional[str] = None

class AdvisoryReport(BaseModel):
    condition_summary: str
    overall_risk: str  # Healthy, Low Risk, Moderate Risk, High Risk, Critical
    risk_score: int  # 0 - 100
    risk_explanation: str
    immediate_action: str
    pesticide_recommendation: PesticideRecommendation
    fertilizer_adjustments: FertilizerAdjustment
    ipm: IPMStrategy
    monitoring: MonitoringPlan
    weather_impact_advisory: str
    sources: List[SourceReference] = []
    disclaimer: str = (
        "AI-generated crop health assessments are decision-support information and should be verified "
        "against field conditions, current agricultural guidance, product labels and expert advice where required."
    )


# --- Dedicated pest object-detection API schemas (separate from disease diagnose) ---
class PestPixelBBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class PestObjectDetectionItem(BaseModel):
    pest: str
    raw_label: str
    confidence: float
    bbox: PestPixelBBox
    class_id: Optional[int] = None


class PestModelMeta(BaseModel):
    provider: str = "huggingface"
    model_id: str
    architecture: Optional[str] = None
    inference_mode: str = "huggingface_yolo"
    confidence_threshold: float = 0.25
    load_seconds: Optional[float] = None
    inference_ms: Optional[float] = None


class PestAdvisoryBrief(BaseModel):
    condition_summary: str
    guidance_available: bool = False
    immediate_action: str = ""
    pesticide_recommendation: Optional[PesticideRecommendation] = None
    sources: List[SourceReference] = []
    disclaimer: str = (
        "AI-estimated preliminary severity — not an agronomic diagnosis. "
        "Chemical guidance is only shown when grounded in curated knowledge."
    )


class PestDetectResponse(BaseModel):
    id: str
    status: str  # pests_detected | no_pest_detected | error
    image_url: str
    crop_hint: Optional[str] = None
    detections: List[PestObjectDetectionItem] = []
    count: int = 0
    image_width: int = 0
    image_height: int = 0
    severity: str = "none"  # none | low | moderate | high
    severity_label: str = "AI-estimated preliminary severity — not an agronomic diagnosis."
    model: PestModelMeta
    advisory: Optional[PestAdvisoryBrief] = None
    created_at: str
    inference_meta: Dict[str, Any] = Field(default_factory=dict)

# --- Consolidated Analysis Schema ---
class AnalysisResponse(BaseModel):
    id: str
    status: str  # completed | rejected | processing | error | model_unavailable
    image_url: str
    crop_detected: bool
    crop: str
    crop_confidence: float
    disease: DiseasePrediction
    pests: List[PestDetectionItem] = []
    weather: Optional[WeatherMetrics] = None
    advisory: Optional[AdvisoryReport] = None
    location: Dict[str, Any] = {}
    validation_status: str = "PENDING"  # PENDING, UNDER_REVIEW, CONFIRMED, CORRECTED, REJECTED
    created_at: str
    inference_meta: Dict[str, Any] = Field(default_factory=dict)
    # Distinguishes image-level model output from estimated field risk
    image_level_result: Optional[Dict[str, Any]] = None
    estimated_field_risk: Optional[Dict[str, Any]] = None

# --- Expert Validation Schemas ---
class ExpertValidationRequest(BaseModel):
    analysis_id: str
    farmer_notes: Optional[str] = None

class ExpertValidationReview(BaseModel):
    status: str  # CONFIRMED, CORRECTED, REJECTED
    confirmed_disease: Optional[str] = None
    confirmed_pest: Optional[str] = None
    expert_notes: str
    treatment_corrections: Optional[str] = None

# --- GIS Hotspot Schemas ---
class HotspotFeatureProperties(BaseModel):
    id: str
    district: str
    state: str
    crop: str
    disease: str
    pest: Optional[str] = None
    risk_level: str
    case_count: int
    farm_count: int
    trend_pct: float
    intensity: float  # 0.0 to 1.0 for heatmaps

class HotspotGeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]  # Point: {"type": "Point", "coordinates": [lng, lat]}
    properties: HotspotFeatureProperties

class HotspotGeoJSON(BaseModel):
    type: str = "FeatureCollection"
    features: List[HotspotGeoJSONFeature]

# --- Admin Analytics Schema ---
class AdminAnalytics(BaseModel):
    total_farmers: int
    total_farms: int
    total_analyses: int
    disease_cases: int
    pest_cases: int
    high_risk_areas: int
    pending_expert_reviews: int
    validation_accuracy_rate: float
    disease_distribution: List[Dict[str, Any]]
    pest_distribution: List[Dict[str, Any]]
    regional_cases: List[Dict[str, Any]]
    timeline_trends: List[Dict[str, Any]]
    data_source: str = "memory"
    is_demo_inflated: bool = False

# --- Assistant Chat Schema ---
class AssistantChatRequest(BaseModel):
    message: str
    crop_context: Optional[str] = None
    analysis_id: Optional[str] = None
    language: Optional[str] = "en"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AssistantChatResponse(BaseModel):
    reply: str
    sources: List[SourceReference] = []
    language: str = "en"
