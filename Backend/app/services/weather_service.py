import time
import logging
import httpx
from typing import Dict, Tuple
from app.models.schemas import WeatherMetrics
from app.core.config import settings

logger = logging.getLogger("cropshield.weather")

_weather_cache: Dict[str, Tuple[float, WeatherMetrics]] = {}
CACHE_TTL = 3600


class WeatherService:
    """Open-Meteo integration with explicit cache / unavailable labeling."""

    async def get_weather(self, lat: float, lon: float) -> WeatherMetrics:
        cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
        now = time.time()

        if cache_key in _weather_cache:
            timestamp, cached_metric = _weather_cache[cache_key]
            if now - timestamp < CACHE_TTL:
                cached_copy = cached_metric.model_copy()
                cached_copy.is_cached = True
                cached_copy.source = "cache"
                return cached_copy

        if settings.USE_MOCK_WEATHER:
            return self._mock_weather()

        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "wind_speed_10m",
                    "cloud_cover",
                ],
                "timezone": "auto",
            }
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(settings.OPEN_METEO_URL, params=params)
                if res.status_code == 200:
                    current = res.json().get("current", {})
                    temp = float(current.get("temperature_2m", 0))
                    rh = float(current.get("relative_humidity_2m", 0))
                    precip = float(current.get("precipitation", 0.0))
                    wind = float(current.get("wind_speed_10m", 0.0))
                    cloud = float(current.get("cloud_cover", 0.0))
                    risk_level, risk_factor = self._evaluate_agro_risk(temp, rh, precip)
                    metric = WeatherMetrics(
                        temperature=round(temp, 1),
                        relative_humidity=round(rh, 1),
                        precipitation=round(precip, 1),
                        wind_speed=round(wind, 1),
                        cloud_cover=round(cloud, 1),
                        risk_level=risk_level,
                        risk_factor=risk_factor,
                        is_cached=False,
                        is_unavailable=False,
                        source="open-meteo",
                    )
                    _weather_cache[cache_key] = (now, metric)
                    return metric
                logger.warning(f"Open-Meteo status {res.status_code}")
        except Exception as e:
            logger.warning(f"Open-Meteo fetch failed ({e})")

        # Prefer labeled cache over silent fake live data
        if cache_key in _weather_cache:
            cached_copy = _weather_cache[cache_key][1].model_copy()
            cached_copy.is_cached = True
            cached_copy.source = "cache"
            cached_copy.risk_factor = f"[CACHED] {cached_copy.risk_factor}"
            return cached_copy

        return self._unavailable_weather()

    def _evaluate_agro_risk(self, temp: float, rh: float, precip: float):
        if rh > 82 and 18 <= temp <= 28:
            return "Critical", "High RH + warm canopy: elevated fungal spore germination pressure."
        if rh > 70 or precip > 2.0:
            return "High", "Elevated foliar disease infection pressure from moisture."
        if rh > 55 and temp > 30:
            return "Moderate", "Warm/moderately dry conditions may favour sucking pests."
        return "Low", "Lower environmental disease propagation pressure."

    def _mock_weather(self) -> WeatherMetrics:
        return WeatherMetrics(
            temperature=27.4,
            relative_humidity=76.0,
            precipitation=0.0,
            wind_speed=9.2,
            cloud_cover=35.0,
            risk_level="Moderate",
            risk_factor="[MOCK WEATHER] USE_MOCK_WEATHER=true — not live Open-Meteo data.",
            is_cached=False,
            is_unavailable=False,
            source="mock",
        )

    def _unavailable_weather(self) -> WeatherMetrics:
        return WeatherMetrics(
            temperature=0.0,
            relative_humidity=0.0,
            precipitation=0.0,
            wind_speed=0.0,
            cloud_cover=0.0,
            risk_level="Unknown",
            risk_factor="Weather unavailable — could not reach Open-Meteo and no valid cache.",
            is_cached=False,
            is_unavailable=True,
            source="unavailable",
        )


weather_service = WeatherService()
