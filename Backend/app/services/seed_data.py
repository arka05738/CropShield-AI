import logging
from datetime import datetime, timezone, timedelta
from app.core.security import get_password_hash
from app.core.database import db, memory_store, persist_user
from app.models.schemas import (
    AnalysisResponse, DiseasePrediction, PestDetectionItem, BoundingBox,
    WeatherMetrics, AdvisoryReport, PesticideRecommendation,
    FertilizerAdjustment, IPMStrategy, MonitoringPlan, SourceReference
)

logger = logging.getLogger("cropshield.seed")

# Development-only accounts. Loaded only when SEED_DEMO_DATA=true and
# ENVIRONMENT != production (see seed_initial_data + startup_checks).
DEMO_USERS = [
    {
        "id": "usr_demo_farmer",
        "email": "demo@cropshield.ai",
        "password_hash": get_password_hash("cropshield123"),
        "full_name": "Ramesh Patel",
        "role": "FARMER",
        "phone": "+91 98765 43210",
        "state": "Maharashtra",
        "district": "Nashik",
        "village": "Dindori",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": "usr_admin",
        "email": "admin@cropshield.ai",
        "password_hash": get_password_hash("cropshield123"),
        "full_name": "Dr. Ananya Sharma",
        "role": "ADMIN",
        "phone": "+91 98200 11223",
        "state": "Delhi",
        "district": "New Delhi",
        "village": "ICAR HQ",
        "created_at": datetime.now(timezone.utc)
    },
    # Manual browser testing (local DEV only)
    {
        "id": "usr_manual_farmer_test",
        "email": "farmer@test.com",
        "password_hash": get_password_hash("Farmer@12345"),
        "full_name": "Manual Test Farmer",
        "role": "FARMER",
        "phone": "+91 90000 11111",
        "state": "Maharashtra",
        "district": "Pune",
        "village": "Test Village",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": "usr_manual_admin_test",
        "email": "admin@test.com",
        "password_hash": get_password_hash("Admin@12345"),
        "full_name": "Manual Test Admin",
        "role": "ADMIN",
        "phone": "+91 90000 22222",
        "state": "Delhi",
        "district": "New Delhi",
        "village": "Test HQ",
        "created_at": datetime.now(timezone.utc)
    },
]

DEMO_ANALYSES = [
    {
        "id": "an_demo_01",
        "user_id": "usr_demo_farmer",
        "status": "completed",
        "image_url": "https://images.unsplash.com/photo-1592878904946-b3cd8ae243d0?auto=format&fit=crop&w=800&q=80",
        "crop_detected": True,
        "crop": "Tomato",
        "crop_confidence": 0.96,
        "disease": {
            "disease": "Early Blight",
            "pathogen_type": "Fungal",
            "confidence": 0.91,
            "description": "Concentric rings (target-like spots) caused by Alternaria solani on lower leaves, progressing upwards."
        },
        "pests": [
            {
                "name": "Aphid",
                "scientific_name": "Aphis gossypii",
                "confidence": 0.94,
                "bbox": {"x": 0.28, "y": 0.22, "width": 0.26, "height": 0.24},
                "severity": "Moderate"
            },
            {
                "name": "Whitefly",
                "scientific_name": "Bemisia tabaci",
                "confidence": 0.86,
                "bbox": {"x": 0.62, "y": 0.48, "width": 0.22, "height": 0.20},
                "severity": "Moderate"
            }
        ],
        "weather": {
            "temperature": 27.5,
            "relative_humidity": 84.0,
            "precipitation": 1.2,
            "wind_speed": 8.5,
            "cloud_cover": 65.0,
            "risk_level": "Critical",
            "risk_factor": "Elevated humidity 84% accelerates foliar spore germination.",
            "is_cached": False
        },
        "advisory": {
            "condition_summary": "Alternaria solani infection characterized by concentric brown target spots on leaves, exacerbated by temperature 24-30°C and frequent dew.",
            "overall_risk": "High Risk",
            "risk_score": 78,
            "risk_explanation": "Early Blight detected (91% confidence). 2 pest clusters observed. High relative humidity (84%) accelerates spore germination.",
            "immediate_action": "Spray Dithane M-45 (Mancozeb 75% WP) @ 2.5 g/L using a calibrated knapsack sprayer during early morning hours.",
            "pesticide_recommendation": {
                "active_ingredient": "Mancozeb 75% WP",
                "chemical_name": "Dithane M-45",
                "exact_dose_per_liter": "2.5 g/L",
                "withholding_period_days": 7,
                "application_method": "Foliar mist with hollow cone nozzle covering upper and lower leaf canopy.",
                "safety_warnings": [
                    "Wear protective mask and nitrile gloves during spraying.",
                    "Do not harvest tomatoes within 7 days of treatment."
                ]
            },
            "fertilizer_adjustments": {
                "n_ratio": "Reduced Nitrogen (-30%)",
                "p_ratio": "Single Super Phosphate 50 kg/ha",
                "k_ratio": "Elevated Potassium (+25% via SOP)",
                "micronutrients": ["Zinc Sulphate 0.5%", "Borax 0.2%"],
                "instructions": "Temporarily suspend excess urea application as succulent vegetative flush increases fungal susceptibility."
            },
            "ipm": {
                "cultural": ["Prune lower blighted leaves showing target lesions.", "Ensure 60x45cm spacing for canopy airflow."],
                "biological": ["Trichoderma viride foliar spray @ 5 g/L.", "Neem Oil 1500 ppm @ 3 ml/L for aphid deterrence."],
                "mechanical": ["Install 15 yellow sticky traps per acre."],
                "chemical": ["Mancozeb 75 WP @ 2.5 g/L. Alternate with Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L if lesions expand."]
            },
            "monitoring": {
                "day_1": "Complete foliar spray across affected block.",
                "day_3": "Check for arrest of lesion margin expansion.",
                "day_7": "Sample 20 plants for new spots.",
                "day_14": "Inspect emergent apical canopy."
            },
            "weather_impact_advisory": "Relative humidity above 80% creates critical spore incubation conditions.",
            "sources": [
                {
                    "title": "Package of Practices for Commercial Solanaceous Crops",
                    "authority": "ICAR-IIHR, Bengaluru",
                    "document_type": "ICAR POP Manual",
                    "page_number": 42
                }
            ],
            "disclaimer": "AI-generated crop health assessments are decision-support information and should be verified against field conditions."
        },
        "location": {"latitude": 19.9975, "longitude": 73.7898, "district": "Nashik", "state": "Maharashtra"},
        "validation_status": "PENDING",
        "is_demo": True,
        "inference_meta": {"disease_inference_mode": "demo_seed", "pest_inference_mode": "demo_seed"},
        "created_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    },
    {
        "id": "an_demo_02",
        "user_id": "usr_demo_farmer",
        "status": "completed",
        "image_url": "https://images.unsplash.com/photo-1574943320219-553eb213f72d?auto=format&fit=crop&w=800&q=80",
        "crop_detected": True,
        "crop": "Rice",
        "crop_confidence": 0.98,
        "disease": {
            "disease": "Rice Blast",
            "pathogen_type": "Fungal",
            "confidence": 0.94,
            "description": "Spindle-shaped lesions with grey centres and brownish margins caused by Magnaporthe oryzae."
        },
        "pests": [
            {
                "name": "Yellow Stem Borer",
                "scientific_name": "Scirpophaga incertulas",
                "confidence": 0.89,
                "bbox": {"x": 0.35, "y": 0.40, "width": 0.30, "height": 0.28},
                "severity": "High"
            }
        ],
        "weather": {
            "temperature": 28.0,
            "relative_humidity": 88.0,
            "precipitation": 3.4,
            "wind_speed": 11.0,
            "cloud_cover": 80.0,
            "risk_level": "Critical",
            "risk_factor": "Monsoon downpours and continuous canopy moisture promote blast progression.",
            "is_cached": False
        },
        "advisory": {
            "condition_summary": "Magnaporthe oryzae foliar blast outbreak with simultaneous stem borer dead hearts.",
            "overall_risk": "Critical",
            "risk_score": 86,
            "risk_explanation": "Rice Blast identified with 94% confidence. Dead-heart tiller damage observed.",
            "immediate_action": "Drain standing water for 24 hours and apply Tricyclazole 75 WP @ 0.6 g/L.",
            "pesticide_recommendation": {
                "active_ingredient": "Tricyclazole 75% WP",
                "chemical_name": "Beam 75 WP",
                "exact_dose_per_liter": "0.6 g/L",
                "withholding_period_days": 30,
                "application_method": "500 L water volume per hectare using motorized mist blower.",
                "safety_warnings": ["Do not drain spray run-off into aquatic channels."]
            },
            "fertilizer_adjustments": {
                "n_ratio": "Split Nitrogen into 3 equal doses; avoid top-dressing on cloudy days",
                "p_ratio": "SSP 60 kg/ha",
                "k_ratio": "MOP 40 kg/ha",
                "micronutrients": ["Calcium Silicate 200 kg/ha"],
                "instructions": "Suspend nitrogenous top-dressing until blast progression halts."
            },
            "ipm": {
                "cultural": ["Drain field water temporarily.", "Burn infected straw margins."],
                "biological": ["Trichogramma japonicum egg parasitoids @ 100,000/ha."],
                "mechanical": ["Erect light traps for stem borer moths."],
                "chemical": ["Tricyclazole 75 WP @ 0.6 g/L."]
            },
            "monitoring": {
                "day_1": "Apply Tricyclazole spray immediately.",
                "day_3": "Count pheromone trap moth catches.",
                "day_7": "Check tiller recovery and flag leaf emergence.",
                "day_14": "Inspect panicles for neck blast."
            },
            "weather_impact_advisory": "High humidity > 85% accelerates blast sporulation.",
            "sources": [
                {
                    "title": "Standard Operating Procedure for Rice Blast & Stem Borer Management",
                    "authority": "ICAR-NRRI, Cuttack",
                    "document_type": "ICAR National SOP",
                    "page_number": 28
                }
            ],
            "disclaimer": "AI-generated crop health assessments are decision-support information."
        },
        "location": {"latitude": 23.4710, "longitude": 88.5492, "district": "Nadia", "state": "West Bengal"},
        "validation_status": "CONFIRMED",
        "is_demo": True,
        "inference_meta": {"disease_inference_mode": "demo_seed", "pest_inference_mode": "demo_seed"},
        "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    },
    {
        "id": "an_demo_03",
        "user_id": "usr_demo_farmer",
        "status": "completed",
        "image_url": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80",
        "crop_detected": True,
        "crop": "Wheat",
        "crop_confidence": 0.99,
        "disease": {
            "disease": "Healthy Crop",
            "pathogen_type": "Healthy",
            "confidence": 0.97,
            "description": "Lush green canopy with vigorous flag leaves and healthy tiller formation."
        },
        "pests": [],
        "weather": {
            "temperature": 21.0,
            "relative_humidity": 58.0,
            "precipitation": 0.0,
            "wind_speed": 6.2,
            "cloud_cover": 10.0,
            "risk_level": "Low",
            "risk_factor": "Optimal temperature and dry canopy.",
            "is_cached": True
        },
        "advisory": {
            "condition_summary": "Wheat crop is in prime vegetative tillering stage with zero visible pathogens.",
            "overall_risk": "Healthy",
            "risk_score": 8,
            "risk_explanation": "Canopy shows vibrant green chlorophyll with balanced turgor pressure.",
            "immediate_action": "Maintain scheduled crown-root initiation (CRI) irrigation. No chemical intervention required.",
            "pesticide_recommendation": {
                "active_ingredient": "None required",
                "chemical_name": "N/A",
                "exact_dose_per_liter": "0",
                "withholding_period_days": 0,
                "application_method": "N/A",
                "safety_warnings": ["Avoid prophylactic chemical sprays on healthy foliage."]
            },
            "fertilizer_adjustments": {
                "n_ratio": "Standard basal NPK 120:60:40 kg/ha",
                "p_ratio": "DAP 60 kg/ha",
                "k_ratio": "MOP 40 kg/ha",
                "micronutrients": ["Zinc Sulphate 25 kg/ha basal"],
                "instructions": "Ensure timely top-dressing with remaining 50% Urea during first irrigation."
            },
            "ipm": {
                "cultural": ["Maintain clean border bunds.", "Scout field weekly for stripe rust pustules."],
                "biological": ["Preserve predatory coccinellid ladybird beetles."],
                "mechanical": ["Yellow sticky cards for aphid monitoring."],
                "chemical": ["Zero chemical spray needed."]
            },
            "monitoring": {
                "day_1": "Routine monitoring.",
                "day_3": "Check soil moisture level.",
                "day_7": "Scout for flag leaf yellowing.",
                "day_14": "Inspect spikelet initiation."
            },
            "weather_impact_advisory": "Dry cool weather is optimal for wheat tillering.",
            "sources": [
                {
                    "title": "ICAR-IIWBR Wheat Crop Management Guide",
                    "authority": "ICAR-IIWBR, Karnal",
                    "document_type": "POP Manual",
                    "page_number": 12
                }
            ],
            "disclaimer": "AI-generated crop health assessments are decision-support information."
        },
        "location": {"latitude": 30.9010, "longitude": 75.8573, "district": "Ludhiana", "state": "Punjab"},
        "validation_status": "CONFIRMED",
        "is_demo": True,
        "inference_meta": {"disease_inference_mode": "demo_seed", "pest_inference_mode": "unavailable"},
        "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
    }
]

async def seed_initial_data():
    """
    Development/test-only seed of known demo accounts and sample analyses.

    Blocked when ENVIRONMENT=production.
    Requires SEED_DEMO_DATA=true explicitly for non-production.
    """
    from app.core.config import settings

    if settings.ENVIRONMENT.lower() == "production":
        logger.warning("Skipping demo seed: ENVIRONMENT=production (known demo passwords must not ship).")
        return

    if not settings.SEED_DEMO_DATA:
        logger.info("Skipping demo seed: SEED_DEMO_DATA is not enabled.")
        return

    for user in DEMO_USERS:
        existing = next((u for u in memory_store["users"] if u.get("email") == user["email"]), None)
        if existing is None:
            memory_store["users"].append(user)
            await persist_user(user)
        else:
            # Local DEV only: refresh known demo password hashes so logins remain
            # compatible after backend image/auth-code upgrades. Does not touch
            # non-demo accounts. Never runs when ENVIRONMENT=production.
            existing["password_hash"] = user["password_hash"]
            await persist_user(existing)

    for an in DEMO_ANALYSES:
        if not any(a["id"] == an["id"] for a in memory_store["analyses"]):
            memory_store["analyses"].append(an)

    logger.warning(
        "DEV SEED ACTIVE: demo users/analyses loaded for local development. "
        "Do not enable SEED_DEMO_DATA in production. "
        "users=%s analyses=%s",
        len(memory_store["users"]),
        len(memory_store["analyses"]),
    )
