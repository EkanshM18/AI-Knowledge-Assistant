from __future__ import annotations

import httpx

from app.bots.general.clients.weather_client import WeatherClient


class WeatherService:
    def __init__(self, weather_client: WeatherClient) -> None:
        self.weather_client = weather_client
        self._weather_code_labels = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            73: "moderate snow",
            75: "heavy snow",
            80: "rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            95: "thunderstorm",
        }

    def lookup(self, location: str | None) -> dict:
        if not location:
            return {
                "tool_name": "weather",
                "status": "needs_input",
                "summary": "Please tell me which city or location you want the weather for.",
                "source_label": "Open-Meteo",
                "source_url": "https://open-meteo.com/en/docs",
            }

        try:
            payload = self.weather_client.lookup(location)
        except httpx.HTTPError:
            return {
                "tool_name": "weather",
                "status": "error",
                "summary": "I could not reach the live weather service right now. Please try again in a moment.",
                "source_label": "Open-Meteo",
                "source_url": "https://open-meteo.com/en/docs",
            }

        results = payload.get("results", [])
        if not results:
            return {
                "tool_name": "weather",
                "status": "not_found",
                "summary": f"I could not find a weather location match for '{location}'.",
                "source_label": "Open-Meteo",
                "source_url": "https://open-meteo.com/en/docs/geocoding-api",
            }

        place = results[0]
        forecast_payload = payload.get("forecast", {})
        current = forecast_payload.get("current", {})
        daily = forecast_payload.get("daily", {})
        description = self._weather_code_labels.get(current.get("weather_code"), "current conditions")
        resolved_name = ", ".join(
            part for part in [place.get("name"), place.get("admin1"), place.get("country")] if part
        )
        summary = (
            f"{resolved_name} is currently {current.get('temperature_2m')}°C with {description}. "
            f"It feels like {current.get('apparent_temperature')}°C, humidity is "
            f"{current.get('relative_humidity_2m')}%, and wind speed is {current.get('wind_speed_10m')} km/h. "
            f"Today's range is {daily.get('temperature_2m_min', ['?'])[0]}°C to "
            f"{daily.get('temperature_2m_max', ['?'])[0]}°C with up to "
            f"{daily.get('precipitation_probability_max', ['?'])[0]}% precipitation chance."
        )
        return {
            "tool_name": "weather",
            "status": "success",
            "summary": summary,
            "source_label": "Open-Meteo",
            "source_url": "https://open-meteo.com/en/docs",
        }
