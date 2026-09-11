from fastapi import APIRouter, Query
from app.models.schemas import WeatherMetrics
from app.services.weather_service import weather_service

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])

@router.get("/current", response_model=WeatherMetrics)
async def get_current_agro_weather(
    latitude: float = Query(19.9975, description="Farm Latitude"),
    longitude: float = Query(73.7898, description="Farm Longitude")
):
    """
    Fetch real-time agro-meteorological parameters from Open-Meteo
    and calculate microclimatic disease propagation risk.
    """
    return await weather_service.get_weather(latitude, longitude)
