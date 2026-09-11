from collections import Counter
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.models.schemas import AdminAnalytics
from app.core.security import require_role, ADMIN_ROLES
from app.core.config import settings
from app.core.database import memory_store, persistence_mode
from app.ml.registry import model_registry

router = APIRouter(prefix="/admin", tags=["Admin Command Center"])

RISK_COLORS = {
    "Healthy": "#10B981",
    "Low": "#34D399",
    "Moderate": "#F59E0B",
    "High": "#F97316",
    "Critical": "#EF4444",
}


def _build_real_analytics() -> AdminAnalytics:
    analyses = memory_store["analyses"]
    validations = memory_store["validations"]
    hotspots = memory_store["hotspots"]
    users = memory_store["users"]
    farms = memory_store["farms"]

    farmers = [u for u in users if u.get("role") == "FARMER"]

    def _disease_name(a: dict) -> str:
        d = a.get("disease") or {}
        name = d.get("disease") if isinstance(d, dict) else None
        return (name or "").strip()

    def _pathogen(a: dict) -> str:
        d = a.get("disease") or {}
        return ((d.get("pathogen_type") if isinstance(d, dict) else None) or "").lower()

    disease_cases = [
        a for a in analyses
        if _pathogen(a) != "healthy"
        and _disease_name(a).lower() not in ("", "healthy crop", "healthy")
    ]
    pest_cases = [a for a in analyses if len(a.get("pests") or []) > 0]
    pest_od_cases = list(memory_store.get("pest_analyses") or [])
    # Prefer dedicated OD history for pest counts when present
    if pest_od_cases:
        pest_cases = pest_od_cases
    high_risk_areas = [
        h for h in hotspots
        if "high" in str(h.get("risk_level", "")).lower()
        or "critical" in str(h.get("risk_level", "")).lower()
    ]
    pending_validations = [v for v in validations if v.get("status") == "PENDING"]
    confirmed = [v for v in validations if v.get("status") == "CONFIRMED"]
    reviewed = [v for v in validations if v.get("status") in ("CONFIRMED", "CORRECTED", "REJECTED")]
    val_accuracy = round((len(confirmed) / len(reviewed) * 100) if reviewed else 0.0, 1)

    disease_counter = Counter(
        name for name in (_disease_name(a) for a in analyses) if name
    )
    disease_dist = [
        {
            "name": name,
            "count": count,
            "category": next(
                (
                    ((a.get("disease") or {}).get("pathogen_type") or "Unknown")
                    for a in analyses
                    if _disease_name(a) == name
                ),
                "Unknown",
            ),
            "color": RISK_COLORS.get("Moderate", "#6366F1"),
        }
        for name, count in disease_counter.most_common(12)
    ]

    pest_counter: Counter = Counter()
    for a in analyses:
        for p in a.get("pests") or []:
            pest_counter[p.get("name", "Unknown")] += 1
    for row in memory_store.get("pest_analyses") or []:
        pest_counter[(row.get("pest") or row.get("raw_label") or "Unknown")] += max(1, int(row.get("count") or 1))
    pest_dist = [{"name": n, "count": c, "color": "#3B82F6"} for n, c in pest_counter.most_common(12)]

    order = ["Healthy", "Low Risk", "Moderate Risk", "High Risk", "Critical"]
    region_counter: Counter = Counter()
    region_risk: dict = {}
    for a in analyses:
        loc = a.get("location") or {}
        region = f"{loc.get('state', 'Unknown')} ({loc.get('district', 'Unknown')})"
        region_counter[region] += 1
        risk = (a.get("advisory") or {}).get("overall_risk") or "Moderate Risk"
        prev = region_risk.get(region, "Healthy")
        prev_i = order.index(prev) if prev in order else 0
        risk_i = order.index(risk) if risk in order else 0
        if risk_i >= prev_i:
            region_risk[region] = risk

    regional_dist = [
        {"region": r, "cases": c, "risk": region_risk.get(r, "Moderate Risk")}
        for r, c in region_counter.most_common(20)
    ]

    # Timeline from actual created_at dates (last 7 buckets by day)
    day_counter: Counter = Counter()
    critical_counter: Counter = Counter()
    for a in analyses:
        created = a.get("created_at") or ""
        day = str(created)[:10] or "unknown"
        day_counter[day] += 1
        risk = (a.get("advisory") or {}).get("overall_risk", "")
        if "Critical" in str(risk) or "High" in str(risk):
            critical_counter[day] += 1
    timeline_trends = [
        {
            "date": day,
            "cases": count,
            "resolved": 0,
            "critical": critical_counter.get(day, 0),
        }
        for day, count in sorted(day_counter.items())[-7:]
    ]

    return AdminAnalytics(
        total_farmers=len(farmers),
        total_farms=len(farms),
        total_analyses=len(analyses),
        disease_cases=len(disease_cases),
        pest_cases=len(pest_cases),
        high_risk_areas=len(high_risk_areas),
        pending_expert_reviews=len(pending_validations),
        validation_accuracy_rate=val_accuracy,
        disease_distribution=disease_dist,
        pest_distribution=pest_dist,
        regional_cases=regional_dist,
        timeline_trends=timeline_trends,
        data_source=persistence_mode(),
        is_demo_inflated=False,
    )


@router.get("/analytics", response_model=AdminAnalytics)
@router.get("/stats", response_model=AdminAnalytics)
async def get_admin_analytics(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    return _build_real_analytics()


@router.get("/models")
async def get_registered_models(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    models = model_registry.get_all()
    return {
        "models": models,
        "count": len(models),
        "note": "Threshold updates are stored in-memory metadata unless wired to loaded weights.",
    }


@router.post("/models/{id}/threshold")
async def update_model_threshold(
    id: str,
    threshold: float = Query(..., ge=0.1, le=1.0),
    current_user: dict = Depends(require_role(ADMIN_ROLES)),
):
    success = model_registry.update_threshold(id, threshold)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Model '{id}' not found")
    return {
        "status": "success",
        "model_id": id,
        "new_threshold": threshold,
        "applied_to_inference": False,
        "message": "Threshold saved in registry metadata. Heuristic pipeline does not load trained weights yet.",
    }


@router.get("/users")
async def get_all_users(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    safe_users = []
    for u in memory_store["users"]:
        safe_users.append({
            "id": u.get("id"),
            "email": u.get("email"),
            "full_name": u.get("full_name"),
            "role": u.get("role"),
            "phone": u.get("phone"),
            "state": u.get("state"),
            "district": u.get("district"),
            "created_at": u.get("created_at"),
        })
    return {"users": safe_users, "count": len(safe_users), "data_source": persistence_mode()}


@router.get("/cases")
@router.get("/analyses")
async def get_all_cases(
    crop: Optional[str] = None,
    current_user: dict = Depends(require_role(ADMIN_ROLES)),
):
    cases = list(memory_store["analyses"])
    if crop and crop.lower() != "all":
        cases = [a for a in cases if str(a.get("crop", "")).lower() == crop.lower()]
    return {"cases": cases, "count": len(cases), "data_source": persistence_mode()}


@router.get("/farms")
async def get_farms(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    return {"farms": memory_store["farms"], "count": len(memory_store["farms"]), "data_source": persistence_mode()}


@router.get("/diseases")
async def get_disease_summary(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    counter = Counter(
        name
        for name in (
            ((a.get("disease") or {}).get("disease") or "").strip()
            for a in memory_store["analyses"]
            if isinstance(a.get("disease"), dict)
        )
        if name
    )
    return {
        "record_type": "disease",
        "diseases": [{"name": n, "count": c} for n, c in counter.most_common()],
        "data_source": persistence_mode(),
    }


@router.get("/pests")
async def get_pest_summary(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    """
    Pest summary for future dashboard — distinct from disease cases.
    Includes dedicated pest OD history plus any legacy diagnose-embedded pests.
    """
    counter: Counter = Counter()
    cases = []

    for row in memory_store.get("pest_analyses", []):
        pest_name = (row.get("pest") or row.get("raw_label") or "").strip() or "Unknown"
        counter[pest_name] += 1
        advisory = row.get("advisory") if isinstance(row.get("advisory"), dict) else {}
        model_obj = row.get("model") if isinstance(row.get("model"), dict) else {}
        cases.append(
            {
                "id": row.get("id"),
                "record_type": "pest",
                "user_id": row.get("user_id"),
                "crop": row.get("crop") or row.get("crop_hint"),
                "pest": pest_name,
                "raw_label": row.get("raw_label"),
                "confidence": row.get("confidence"),
                "count": row.get("count"),
                "severity": row.get("severity"),
                "severity_label": row.get("severity_label"),
                "model": row.get("model_id") or model_obj.get("model_id"),
                "model_id": row.get("model_id") or model_obj.get("model_id"),
                "model_meta": model_obj or None,
                "timestamp": row.get("created_at"),
                "created_at": row.get("created_at"),
                "image_url": row.get("image_url"),
                "detections": row.get("detections") or [],
                "image_width": row.get("image_width"),
                "image_height": row.get("image_height"),
                "advisory": {
                    "guidance_available": bool(
                        advisory.get("guidance_available")
                        if advisory
                        else row.get("guidance_available")
                    ),
                    "condition_summary": advisory.get("condition_summary") if advisory else None,
                },
                "status": row.get("status"),
            }
        )

    # Legacy diagnose-embedded pests (mock/empty path) — keep visible but labeled
    for a in memory_store.get("analyses", []):
        for p in a.get("pests") or []:
            name = (p.get("name") if isinstance(p, dict) else None) or "Unknown"
            counter[name] += 1

    return {
        "record_type": "pest",
        "pests": [{"name": n, "count": c} for n, c in counter.most_common()],
        "cases": cases,
        "pest_od_cases": len(memory_store.get("pest_analyses", [])),
        "mock_pest_mode": bool(settings.USE_MOCK_PEST),
        "pest_model_id": settings.PEST_HF_MODEL_ID if settings.USE_PEST_HF_MODEL else None,
        "note": (
            "Dedicated pest OD history from POST /api/v1/pests/detect. "
            "Disease analyses remain under /admin/diseases and /admin/cases."
        ),
        "data_source": persistence_mode(),
    }
