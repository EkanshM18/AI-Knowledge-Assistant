from __future__ import annotations

import re
from xml.etree import ElementTree

import httpx

from app.core.config import Settings


class NewsClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def fetch(self, topic: str | None = None) -> list[dict]:
        entries: list[dict] = []
        with httpx.Client(timeout=self.settings.http_timeout_seconds) as client:
            for feed_url in self.settings.news_feed_url_list:
                response = client.get(feed_url)
                response.raise_for_status()
                root = ElementTree.fromstring(response.text)
                for item in root.findall(".//item"):
                    title = (item.findtext("title") or "").strip()
                    description = re.sub(r"<[^>]+>", "", (item.findtext("description") or "").strip())
                    link = (item.findtext("link") or "").strip()
                    pub_date = (item.findtext("pubDate") or "").strip()
                    blob = f"{title} {description}".lower()
                    if topic and topic not in blob:
                        continue
                    entries.append(
                        {
                            "title": title,
                            "description": description,
                            "link": link,
                            "published_at": pub_date,
                            "source_feed": feed_url,
                        }
                    )
        return entries

