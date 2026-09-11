import logging
from typing import List, Dict, Any, Optional
from app.models.schemas import HotspotGeoJSON, HotspotGeoJSONFeature, HotspotFeatureProperties
from app.core.database import db, memory_store

logger = logging.getLogger("cropshield.gis.hotspot")

# Curated benchmark agricultural districts across India with authentic geospatial coordinates
INITIAL_HOTSPOTS = [
    {
        "id": "hs_nashik_01",
        "district": "Nashik",
        "state": "Maharashtra",
        "crop": "Tomato",
        "disease": "Early Blight",
        "pest": "Whitefly",
        "risk_level": "High Risk",
        "case_count": 142,
        "farm_count": 87,
        "trend_pct": 23.5,
        "intensity": 0.85,
        "coordinates": [73.7898, 19.9975]  # [lng, lat]
    },
    {
        "id": "hs_nadia_02",
        "district": "Nadia",
        "state": "West Bengal",
        "crop": "Rice",
        "disease": "Rice Blast",
        "pest": "Yellow Stem Borer",
        "risk_level": "Critical",
        "case_count": 215,
        "farm_count": 134,
        "trend_pct": 38.2,
        "intensity": 0.95,
        "coordinates": [88.5492, 23.4710]
    },
    {
        "id": "hs_ludhiana_03",
        "district": "Ludhiana",
        "state": "Punjab",
        "crop": "Wheat",
        "disease": "Yellow Stripe Rust",
        "pest": "Wheat Aphid",
        "risk_level": "Moderate Risk",
        "case_count": 78,
        "farm_count": 52,
        "trend_pct": -4.2,
        "intensity": 0.60,
        "coordinates": [75.8573, 30.9010]
    },
    {
        "id": "hs_guntur_04",
        "district": "Guntur",
        "state": "Andhra Pradesh",
        "crop": "Cotton",
        "disease": "Cotton Leaf Curl Virus",
        "pest": "American Bollworm",
        "risk_level": "Critical",
        "case_count": 189,
        "farm_count": 110,
        "trend_pct": 41.5,
        "intensity": 0.92,
        "coordinates": [80.4365, 16.3067]
    },
    {
        "id": "hs_agra_05",
        "district": "Agra",
        "state": "Uttar Pradesh",
        "crop": "Potato",
        "disease": "Late Blight",
        "pest": "Potato Tuber Moth",
        "risk_level": "High Risk",
        "case_count": 126,
        "farm_count": 79,
        "trend_pct": 19.0,
        "intensity": 0.82,
        "coordinates": [78.0081, 27.1767]
    },
    {
        "id": "hs_karnal_06",
        "district": "Karnal",
        "state": "Haryana",
        "crop": "Rice",
        "disease": "Bacterial Leaf Blight",
        "pest": "Brown Plant Hopper",
        "risk_level": "Moderate Risk",
        "case_count": 64,
        "farm_count": 45,
        "trend_pct": 2.1,
        "intensity": 0.55,
        "coordinates": [76.9897, 29.6857]
    },
    {
        "id": "hs_dharwad_07",
        "district": "Dharwad",
        "state": "Karnataka",
        "crop": "Cotton",
        "disease": "Alternaria Leaf Spot",
        "pest": "Pink Bollworm",
        "risk_level": "High Risk",
        "case_count": 105,
        "farm_count": 68,
        "trend_pct": 14.8,
        "intensity": 0.78,
        "coordinates": [75.0078, 15.4589]
    }
]

class HotspotService:
    """
    Agricultural Geospatial Intelligence Service.
    Calculates disease & pest cluster densities, velocity, and GeoJSON features.
    """
    def __init__(self):
        # Pre-seed in memory if needed
        if not memory_store["hotspots"]:
            memory_store["hotspots"] = list(INITIAL_HOTSPOTS)

    async def get_hotspots_geojson(
        self,
        crop: Optional[str] = None,
        disease: Optional[str] = None,
        state: Optional[str] = None,
        min_risk: Optional[str] = None
    ) -> HotspotGeoJSON:
        features: List[HotspotGeoJSONFeature] = []
        raw_items = memory_store["hotspots"]

        for item in raw_items:
            # Apply filters
            if crop and crop.lower() != "all" and item["crop"].lower() != crop.lower():
                continue
            if disease and disease.lower() != "all" and disease.lower() not in item["disease"].lower():
                continue
            if state and state.lower() != "all" and state.lower() not in item["state"].lower():
                continue
            if min_risk and min_risk.lower() != "all" and item["risk_level"].lower() != min_risk.lower():
                continue

            feature = HotspotGeoJSONFeature(
                geometry={
                    "type": "Point",
                    "coordinates": item["coordinates"]  # [longitude, latitude]
                },
                properties=HotspotFeatureProperties(
                    id=item["id"],
                    district=item["district"],
                    state=item["state"],
                    crop=item["crop"],
                    disease=item["disease"],
                    pest=item.get("pest"),
                    risk_level=item["risk_level"],
                    case_count=item["case_count"],
                    farm_count=item["farm_count"],
                    trend_pct=item["trend_pct"],
                    intensity=item["intensity"]
                )
            )
            features.append(feature)

        return HotspotGeoJSON(features=features)

    def record_case_geospatial(self, lat: float, lng: float, crop: str, disease: str, risk_level: str):
        # Increment nearby hotspot or register new geospatial cluster
        found = False
        for hs in memory_store["hotspots"]:
            hs_lng, hs_lat = hs["coordinates"]
            # Within ~0.5 degree distance (~50km)
            if abs(hs_lat - lat) < 0.6 and abs(hs_lng - lng) < 0.6:
                hs["case_count"] += 1
                hs["intensity"] = min(1.0, hs["intensity"] + 0.02)
                found = True
                break
        
        if not found:
            memory_store["hotspots"].append({
                "id": f"hs_{len(memory_store['hotspots'])+1}",
                "district": "Local Area",
                "state": "Regional",
                "crop": crop,
                "disease": disease,
                "pest": None,
                "risk_level": risk_level,
                "case_count": 1,
                "farm_count": 1,
                "trend_pct": 100.0,
                "intensity": 0.5,
                "coordinates": [lng, lat]
            })

hotspot_service = HotspotService()
