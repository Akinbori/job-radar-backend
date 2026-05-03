from __future__ import annotations

from datetime import datetime, timezone
import os
import httpx

from app.models import RawItem


BLOCKED_TERMS = [
    "india",
    "bangalore",
    "bengaluru",
    "mumbai",
    "delhi",
    "gurgaon",
    "hyderabad",
    "pune",
    "chennai",
    "noida",
]

SEARCH_QUERIES = [
    'site:linkedin.com/posts ("we are hiring" OR "I am hiring" OR "we\'re hiring") ("content marketer" OR "growth marketer" OR "email marketer" OR "lifecycle marketer") -India',
    'site:linkedin.com/posts ("looking for" OR "know anyone" OR "referral") ("content marketer" OR "growth marketer" OR "marketing manager") remote -India',
    'site:x.com ("we are hiring" OR "I am hiring" OR "we\'re hiring") ("content marketer" OR "growth marketer" OR "email marketer") -India',
    'site:twitter.com ("looking for" OR "know anyone" OR "hiring") ("content marketer" OR "growth marketer" OR "lifecycle marketer") remote -India',
    '"looking for a content marketer" remote -India',
    '"hiring content marketer" remote -India',
    '"looking for a growth marketer" remote -India',
    '"hiring growth marketer" remote -India',
    '"hiring email marketer" remote -India',
    '"lifecycle marketing" "hiring" remote -India',
    '"demand generation" "hiring" remote -India',
    '"marketing manager" "remote" "hiring" -India',
]


def _is_blocked(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in BLOCKED_TERMS)


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

                    combined = f"{title} {snippet} {link}"

                    if not link or _is_blocked(combined):
                        continue

                    source = "google_serpapi"
                    if "linkedin.com" in link:
                        source = "linkedin_post"
                    elif "x.com" in link or "twitter.com" in link:
                        source = "x_post"

                    items.append(
                        RawItem(
                            source=source,
                            source_type="social_post",
                            url=link,
                            title=title,
                            body=snippet,
                            company="unknown",
                            posted_at=datetime.now(timezone.utc),
                            location="remote/global preferred",
                            remote_text="remote/global preferred",
                            salary_text=None,
                            employment_type="unknown",
                        )
                    )

        return items
