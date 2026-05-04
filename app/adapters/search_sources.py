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

    roles = [
        "content marketer",
        "content marketing manager",
        "growth marketer",
        "growth marketing manager",
        "email marketer",
        "lifecycle marketer",
        "demand generation marketer",
        "b2b marketer",
        "saas marketer",
        "marketing manager",
    ]

    intent_phrases = [
        "we are hiring",
        "we're hiring",
        "I am hiring",
        "I'm hiring",
        "looking for",
        "need a",
        "know anyone",
        "referral",
        "email me",
        "apply here",
    ]

    queries = []

    for role in roles:
        for phrase in intent_phrases:
            queries.append(f'"{phrase}" "{role}" remote after:{cutoff} -India')

    queries.extend([
        f'site:linkedin.com/posts ("we are hiring" OR "I am hiring" OR "looking for" OR "know anyone") ("content marketer" OR "growth marketer" OR "lifecycle marketer") after:{cutoff} -India',
        f'site:linkedin.com/posts ("DM me" OR "email me" OR "apply here") ("marketing manager" OR "growth marketing" OR "content marketing") after:{cutoff} -India',
        f'site:x.com ("we are hiring" OR "I am hiring" OR "looking for" OR "know anyone") ("content marketer" OR "growth marketer" OR "email marketer") after:{cutoff} -India',
        f'site:twitter.com ("DM me" OR "email me" OR "apply here") ("marketing manager" OR "lifecycle marketing" OR "demand generation") after:{cutoff} -India',
    ])

    return queries


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
                            posted_at=None,
                            date_found=datetime.now(timezone.utc),
                            location="remote/global preferred",
                            remote_text="remote/global preferred",
                            salary_text=None,
                            employment_type="unknown",
                        )
                    )

        return items
