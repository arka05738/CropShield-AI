from typing import Optional
from fastapi import APIRouter, Depends
from app.models.schemas import HotspotGeoJSON
from app.services.hotspot_service import hotspot_service
from app.core.security import require_role, ADMIN_ROLES, get_current_user
from app.core.database import memory_store, persistence_mode

router = APIRouter(tags=["Geospatial Intelligence"])


@router.get("/gis/hotspots", response_model=HotspotGeoJSON)
@router.get("/admin/hotspots", response_model=HotspotGeoJSON)
async def get_geospatial_hotspots(
    crop: Optional[str] = None,
    disease: Optional[str] = None,
    state: Optional[str] = None,
    min_risk: Optional[str] = None,
    current_user: dict = Depends(require_role(ADMIN_ROLES)),
):
    """Hotspots derived from seeded + recorded cases (not fabricated live outbreak feeds)."""
    return await hotspot_service.get_hotspots_geojson(
        crop=crop,
        disease=disease,
        state=state,
        min_risk=min_risk,
    )


@router.get("/gis/cases")
async def get_recent_spatial_cases(current_user: dict = Depends(require_role(ADMIN_ROLES))):
    cases = []
    for an in memory_store["analyses"]:
        loc = an.get("location", {})
        if loc.get("latitude") is not None and loc.get("longitude") is not None:
            cases.append({
                "id": an["id"],
                "crop": an.get("crop"),
                "disease": (an.get("disease") or {}).get("disease"),
                "risk_level": (an.get("advisory") or {}).get("overall_risk", "Moderate"),
                "coordinates": [loc["longitude"], loc["latitude"]],
                "created_at": an.get("created_at"),
                "is_demo": an.get("is_demo", False),
            })
    return {"cases": cases, "count": len(cases), "data_source": persistence_mode()}
