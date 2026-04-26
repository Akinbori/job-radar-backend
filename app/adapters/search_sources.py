from __future__ import annotations

from datetime import datetime, timezone
import os
import httpx

from app.models import RawItem


SEARCH_QUERIES = [
    '"looking for a content marketer"',
    '"looking for content marketer"',
    '"hiring content marketer"',
    '"need a content marketer"',
    '"know anyone" "content marketer"',
    '"looking for a growth marketer"',
    '"hiring growth marketer"',
    '"need a growth marketer"',
    '"know anyone" "growth marketer"',
    '"looking for an email marketer"',
    '"hiring email marketer"',
    '"need an email marketer"',
    '"lifecycle marketing" "hiring"',
    '"demand generation" "hiring"',
    '"marketing manager" "remote" "hiring"',
    '"content marketing manager" "remote"',
    '"growth marketing manager" "remote"',
]


class SerpApiHiringSignalAdapter:
    name = "serpapi_hiring_signals"

    def __init__(self) -> None:
        self.api_key = os.getenv("SERPAPI_API_KEY")

    def fetch(self) -> list[RawItem]:
        if not self.api_key:
            return []

        items: list[RawItem] = []

        with httpx.Client(timeout=30.0) as client:
            for query in SEARCH_QUERIES:
                try:
                    response = client.get(
                        "https://serpapi.com/search.json",
                        params={
                            "engine": "google",
                            "q": query,
                            "api_key": self.api_key,
                            "num": 10,
                        },
                    )
                    data = response.json()
                except Exception:
                    continue

                for result in data.get("organic_results", []):
                    title = result.get("title") or ""
                    snippet = result.get("snippet") or ""
                    link = result.get("link") or ""

                    if not link:
                        continue

                    items.append(
                        RawItem(
                            source="google_serpapi",
                            source_type="search_result",
                            url=link,
                            title=title,
                            body=snippet,
                            company="unknown",
                            posted_at=datetime.now(timezone.utc),
                            location="unknown",
                            remote_text="unknown",
                            salary_text=None,
                            employment_type="unknown",
                        )
                    )

        return items
