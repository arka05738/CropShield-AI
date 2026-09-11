import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.models.schemas import ExpertValidationRequest, ExpertValidationReview
from app.core.database import memory_store, persist_validation, update_analysis_fields

logger = logging.getLogger("cropshield.validation")

INITIAL_VALIDATIONS = [
    {
        "id": "val_101",
        "analysis_id": "an_demo_01",
        "farmer_name": "Suresh Kale",
        "farmer_email": "suresh.kale@agri.in",
        "farmer_phone": "+91 94221 00219",
        "farmer_notes": "Spots appeared after rainy days. DEMO seed case.",
        "district": "Nashik",
        "state": "Maharashtra",
        "crop": "Tomato",
        "ai_predicted_disease": "Early Blight",
        "ai_confidence": 0.91,
        "ai_risk_level": "High Risk",
        "image_url": "/uploads/sample_tomato_early_blight.jpg",
        "status": "PENDING",
        "created_at": "2026-09-05T10:30:00Z",
        "reviewer_id": None,
        "reviewed_at": None,
        "confirmed_disease": None,
        "expert_notes": None,
        "is_demo": True,
    },
    {
        "id": "val_102",
        "analysis_id": "an_demo_02",
        "farmer_name": "Harpreet Singh",
        "farmer_email": "harpreet.singh@punjabagro.org",
        "farmer_phone": "+91 98140 55432",
        "farmer_notes": "Yellow stripe powder on flag leaf. DEMO seed case.",
        "district": "Ludhiana",
        "state": "Punjab",
        "crop": "Wheat",
        "ai_predicted_disease": "Yellow Stripe Rust",
        "ai_confidence": 0.88,
        "ai_risk_level": "Moderate Risk",
        "image_url": "/uploads/sample_wheat_rust.jpg",
        "status": "UNDER_REVIEW",
        "created_at": "2026-09-04T16:15:00Z",
        "reviewer_id": "exp_dr_verma",
        "reviewed_at": None,
        "confirmed_disease": None,
        "expert_notes": "Microscopic review in progress.",
        "is_demo": True,
    },
    {
        "id": "val_103",
        "analysis_id": "an_demo_02",
        "farmer_name": "Subhash Ghosh",
        "farmer_email": "s.ghosh@bengalfarm.in",
        "farmer_phone": "+91 94340 12890",
        "farmer_notes": "Spindle lesions. DEMO seed case.",
        "district": "Nadia",
        "state": "West Bengal",
        "crop": "Rice",
        "ai_predicted_disease": "Rice Blast",
        "ai_confidence": 0.94,
        "ai_risk_level": "Critical",
        "image_url": "/uploads/sample_rice_blast.jpg",
        "status": "CONFIRMED",
        "created_at": "2026-09-03T09:00:00Z",
        "reviewer_id": "exp_dr_sen",
        "reviewed_at": "2026-09-03T14:20:00Z",
        "confirmed_disease": "Rice Blast",
        "expert_notes": "Confirmed blast. Ground-truth stored for future model improvement (no auto-retrain).",
        "is_demo": True,
    },
]


class ValidationService:
    def __init__(self):
        if not memory_store["validations"]:
            memory_store["validations"] = list(INITIAL_VALIDATIONS)

    async def request_validation(self, req: ExpertValidationRequest, user: dict) -> Dict[str, Any]:
        analysis = next((a for a in memory_store["analyses"] if a["id"] == req.analysis_id), None)
        if not analysis:
            raise ValueError(f"Analysis '{req.analysis_id}' not found")

        if analysis.get("user_id") != user.get("id") and user.get("role") == "FARMER":
            raise PermissionError("Cannot request validation for another user's analysis")

        disease = analysis.get("disease") or {}
        advisory = analysis.get("advisory") or {}
        val_id = f"val_{len(memory_store['validations']) + 200}"
        new_record = {
            "id": val_id,
            "analysis_id": req.analysis_id,
            "farmer_name": user.get("full_name") or user.get("name") or "Farmer",
            "farmer_email": user.get("email"),
            "farmer_phone": user.get("phone"),
            "farmer_notes": req.farmer_notes or "Farmer requested expert review.",
            "district": (analysis.get("location") or {}).get("district") or user.get("district"),
            "state": (analysis.get("location") or {}).get("state") or user.get("state"),
            "crop": analysis.get("crop"),
            "ai_predicted_disease": disease.get("disease"),
            "ai_confidence": disease.get("confidence"),
            "ai_risk_level": advisory.get("overall_risk"),
            "image_url": analysis.get("image_url"),
            "status": "PENDING",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "reviewer_id": None,
            "reviewed_at": None,
            "confirmed_disease": None,
            "expert_notes": None,
            "is_demo": False,
        }
        await persist_validation(new_record)
        await update_analysis_fields(req.analysis_id, {"validation_status": "PENDING"})
        return new_record

    async def get_queue(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        items = memory_store["validations"]
        if status and status.upper() != "ALL":
            return [v for v in items if v["status"].upper() == status.upper()]
        return items

    async def review_validation(
        self, val_id: str, review: ExpertValidationReview, reviewer: dict
    ) -> Optional[Dict[str, Any]]:
        for val in memory_store["validations"]:
            if val["id"] == val_id:
                status_val = review.status.upper()
                if status_val not in ("CONFIRMED", "CORRECTED", "REJECTED", "UNDER_REVIEW"):
                    raise ValueError("Invalid validation status")
                val["status"] = status_val
                val["confirmed_disease"] = review.confirmed_disease or val.get("ai_predicted_disease")
                val["confirmed_pest"] = review.confirmed_pest
                val["expert_notes"] = review.expert_notes
                val["treatment_corrections"] = review.treatment_corrections
                val["reviewer_id"] = reviewer.get("id", "admin")
                val["reviewed_at"] = datetime.now(timezone.utc).isoformat()
                await persist_validation(val)
                # Store ground truth on analysis — do NOT auto-retrain
                await update_analysis_fields(
                    val["analysis_id"],
                    {
                        "validation_status": status_val,
                        "ground_truth": {
                            "status": status_val,
                            "confirmed_disease": val["confirmed_disease"],
                            "confirmed_pest": review.confirmed_pest,
                            "expert_notes": review.expert_notes,
                            "reviewer_id": val["reviewer_id"],
                            "reviewed_at": val["reviewed_at"],
                            "auto_retrain": False,
                        },
                    },
                )
                return val
        return None


validation_service = ValidationService()
