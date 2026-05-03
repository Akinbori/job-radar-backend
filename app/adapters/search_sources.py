from __future__ import annotations

from datetime import datetime, timezone, timedelta
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


def _is_blocked(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in BLOCKED_TERMS)


def build_search_queries() -> list[str]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%d")

    return [
        f'site:linkedin.com/posts ("we are hiring" OR "I am hiring" OR "we\'re hiring") ("content marketer" OR "growth marketer" OR "email marketer" OR "lifecycle marketer") after:{cutoff} -India',
        f'site:linkedin.com/posts ("looking for" OR "know anyone" OR "referral") ("content marketer" OR "growth marketer" OR "marketing manager") remote after:{cutoff} -India',
        f'site:x.com ("we are hiring" OR "I am hiring" OR "we\'re hiring") ("content marketer" OR "growth marketer" OR "email marketer") after:{cutoff} -India',
        f'site:twitter.com ("looking for" OR "know anyone" OR "hiring") ("content marketer" OR "growth marketer" OR "lifecycle marketer") remote after:{cutoff} -India',
        f'"looking for a content marketer" remote after:{cutoff} -India',
        f'"hiring content marketer" remote after:{cutoff} -India',
        f'"looking for a growth marketer" remote after:{cutoff} -India',
        f'"hiring growth marketer" remote after:{cutoff} -India',
        f'"hiring email marketer" remote after:{cutoff} -India',
        f'"lifecycle marketing" "hiring" remote after:{cutoff} -India',
        f'"demand generation" "hiring" remote after:{cutoff} -India',
        f'"marketing manager" "remote" "hiring" after:{cutoff} -India',
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
            for query in build_search_queries():
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
                            posted_at=None,  # CRITICAL FIX: don't fake freshness
                            date_found=datetime.now(timezone.utc),  # track discovery time
                            location="remote/global preferred",
                            remote_text="remote/global preferred",
                            salary_text=None,
                            employment_type="unknown",
                        )
                    )

        return items
