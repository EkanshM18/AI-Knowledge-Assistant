from __future__ import annotations

from datetime import datetime
import re
from xml.etree import ElementTree
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from app.bots.general.clients.news_client import NewsClient
from app.bots.general.services.joke import JokeService
from app.bots.general.services.weather import WeatherService
from app.core.config import Settings


class GeneralToolService:
    def __init__(
        self,
        settings: Settings,
        weather_service: WeatherService,
        news_client: NewsClient,
        joke_service: JokeService,
    ) -> None:
        self.settings = settings
        self.weather_service = weather_service
        self.news_client = news_client
        self.joke_service = joke_service

    def detect_intent(self, question: str) -> tuple[str, dict]:
        text = question.strip().lower()
        if any(token in text for token in ["joke", "funny", "make me laugh"]):
            return "joke", {}
        if any(token in text for token in ["weather", "forecast", "temperature", "rain", "humidity", "wind"]):
            return "weather", {"location": self._extract_location(question)}
        if any(token in text for token in ["time", "date", "day", "clock"]):
            return "time", {"timezone": self._extract_timezone(question)}
        if any(token in text for token in ["news", "headline", "headlines", "current events", "latest"]):
            return "news", {"topic": self._extract_topic(question)}
        return "conversation", {}

    def execute(self, tool_name: str, tool_input: dict) -> dict:
        handlers = {
            "joke": self._joke_tool,
            "weather": self._weather_tool,
            "time": self._time_tool,
            "news": self._news_tool,
        }
        handler = handlers.get(tool_name)
        if handler is None:
            return {
                "tool_name": tool_name or "conversation",
                "status": "unsupported",
                "summary": "No tool matched this request.",
                "source_label": "Local",
                "source_url": "",
            }
        return handler(tool_input)

    def _joke_tool(self, _: dict) -> dict:
        return self.joke_service.tell()

    def _time_tool(self, tool_input: dict) -> dict:
        requested_timezone = tool_input.get("timezone")
        zone_name = self._resolve_timezone(requested_timezone) if requested_timezone else None

        if requested_timezone and zone_name is None:
            return {
                "tool_name": "time",
                "status": "needs_input",
                "summary": (
                    "I can give time for your local system clock or a clear timezone like "
                    "`UTC` or `Asia/Kolkata`. Please rephrase with a timezone."
                ),
                "source_label": "System clock",
                "source_url": "",
            }

        if zone_name:
            now = datetime.now(ZoneInfo(zone_name))
            timezone_label = zone_name
        else:
            now = datetime.now().astimezone()
            timezone_label = "local system time"

        summary = f"The current time in {timezone_label} is {now.strftime('%A, %d %B %Y %I:%M %p %Z')}."
        return {
            "tool_name": "time",
            "status": "success",
            "summary": summary,
            "source_label": "System clock",
            "source_url": "",
        }

    def _weather_tool(self, tool_input: dict) -> dict:
        return self.weather_service.lookup(tool_input.get("location"))

    def _news_tool(self, tool_input: dict) -> dict:
        topic = (tool_input.get("topic") or "").strip().lower()
        try:
            entries = self.news_client.fetch(topic=topic or None)
        except (httpx.HTTPError, ElementTree.ParseError):
            return {
                "tool_name": "news",
                "status": "error",
                "summary": "I could not reach the live news feeds right now. Please try again in a moment.",
                "source_label": "Configured RSS feeds",
                "source_url": "",
            }

        unique_entries: list[dict] = []
        seen_titles: set[str] = set()
        for entry in entries:
            normalized = entry["title"].lower()
            if normalized in seen_titles:
                continue
            seen_titles.add(normalized)
            unique_entries.append(entry)
            if len(unique_entries) == 5:
                break

        if not unique_entries:
            qualifier = f" about '{topic}'" if topic else ""
            return {
                "tool_name": "news",
                "status": "not_found",
                "summary": f"I could not find recent headlines{qualifier} in the configured feeds.",
                "source_label": "Configured RSS feeds",
                "source_url": "",
            }

        topic_prefix = f" on {topic}" if topic else ""
        lines = [f"Here are the latest headlines{topic_prefix}:"]
        for index, entry in enumerate(unique_entries, start=1):
            lines.append(f"{index}. {entry['title']}")
        return {
            "tool_name": "news",
            "status": "success",
            "summary": "\n".join(lines),
            "source_label": "Configured RSS feeds",
            "source_url": unique_entries[0]["link"],
            "data": {"articles": unique_entries},
        }

    def _extract_location(self, question: str) -> str | None:
        patterns = [
            r"\b(?:in|for|at)\s+([A-Za-z][A-Za-z\s,.-]{1,50})",
            r"\bweather\s+([A-Za-z][A-Za-z\s,.-]{1,50})",
        ]
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip(" ?.,")
                if candidate:
                    return candidate
        return None

    def _extract_topic(self, question: str) -> str | None:
        patterns = [
            r"\b(?:news|headlines|latest)\s+(?:about|on|for)\s+([A-Za-z0-9\s-]{2,50})",
            r"\blatest\s+([A-Za-z0-9\s-]{2,50})\s+news\b",
            r"\babout\s+([A-Za-z0-9\s-]{2,50})",
            r"\bon\s+([A-Za-z0-9\s-]{2,50})",
        ]
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return match.group(1).strip(" ?.,")
        return None

    def _extract_timezone(self, question: str) -> str | None:
        match = re.search(r"\b(?:in|for)\s+([A-Za-z/_+\-]{2,40})", question, re.IGNORECASE)
        return match.group(1).strip(" ?.,") if match else None

    def _resolve_timezone(self, value: str | None) -> str | None:
        if not value:
            return None

        cleaned = value.strip()
        aliases = {
            "utc": "UTC",
            "gmt": "Etc/GMT",
            "ist": "Asia/Kolkata",
            "est": "America/New_York",
            "pst": "America/Los_Angeles",
            "cst": "America/Chicago",
        }
        candidate = aliases.get(cleaned.lower(), cleaned)

        try:
            ZoneInfo(candidate)
            return candidate
        except ZoneInfoNotFoundError:
            return None
