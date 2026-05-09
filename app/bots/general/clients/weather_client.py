from __future__ import annotations

import httpx

from app.core.config import Settings


class WeatherClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def lookup(self, location: str) -> dict:
        with httpx.Client(timeout=self.settings.http_timeout_seconds) as client:
            geo_response = client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location, "count": 1, "language": "en", "format": "json"},
            )
            geo_response.raise_for_status()
            geo_payload = geo_response.json()
            results = geo_payload.get("results", [])
            if not results:
                return {"results": [], "forecast": {}}

            place = results[0]
            forecast_response = client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current": (
                        "temperature_2m,apparent_temperature,relative_humidity_2m,"
                        "weather_code,wind_speed_10m"
                    ),
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "forecast_days": 1,
                    "timezone": "auto",
                },
            )
            forecast_response.raise_for_status()
            return {"results": results, "forecast": forecast_response.json()}

