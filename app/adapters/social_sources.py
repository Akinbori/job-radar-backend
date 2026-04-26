from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import httpx

from app.models import RawItem


SOCIAL_QUERIES = [
    '"looking for" "content marketer"',
    '"hiring" "content marketer"',
    '"looking for" "growth marketer"',
    '"hiring" "growth marketer"',
    '"looking for" "email marketer"',
    '"hiring" "email marketer"',
    '"looking for" "marketing manager"',
    '"hiring" "marketing manager"',
    '"looking for" "lifecycle marketer"',
    '"hiring" "lifecycle marketing"',
    '"need a content marketer"',
    '"need a growth marketer"',
    '"need an email marketer"',
    '"know anyone" "content marketer"',
    '"know anyone" "growth marketer"',
    '"know anyone" "email marketer"',
]


class RedditHiringSignalAdapter:
    name = "reddit_social_hiring"

    def fetch(self) -> list[RawItem]:
        items: list[RawItem] = []

        headers = {
            "User-Agent": "bayo-job-radar/1.0"
        }

        with httpx.Client(timeout=20.0, headers=headers) as client:
            for query in SOCIAL_QUERIES:
                url = "https://www.reddit.com/search.json"
                params = {
                    "q": query,
                    "sort": "new",
                    "limit": 10,
                    "t": "week",
                }

                try:
                    data = client.get(url, params=params).json()
                except Exception:
                    continue

                posts = data.get("data", {}).get("children", [])

                for post in posts:
                    p = post.get("data", {})
                    title = p.get("title") or ""
                    body = p.get("selftext") or ""
                    permalink = p.get("permalink") or ""
                    created = p.get("created_utc")

                    posted_at = (
                        datetime.fromtimestamp(created, tz=timezone.utc)
                        if created
                        else datetime.now(timezone.utc)
                    )

                    items.append(
                        RawItem(
                            source="reddit",
                            source_type="social_post",
                            url=f"https://www.reddit.com{permalink}",
                            title=title,
                            body=body,
                            company="unknown",
                            posted_at=posted_at,
                            location="unknown",
                            remote_text="unknown",
                            salary_text=None,
                            employment_type="unknown",
                        )
                    )

        return items


class HackerNewsHiringSignalAdapter:
    name = "hn_social_hiring"

    def fetch(self) -> list[RawItem]:
        items: list[RawItem] = []

        with httpx.Client(timeout=20.0) as client:
            for query in SOCIAL_QUERIES:
                url = "https://hn.algolia.com/api/v1/search_by_date"
                params = {
                    "query": query,
                    "tags": "story,comment",
                    "hitsPerPage": 10,
                }

                try:
                    data: dict[str, Any] = client.get(url, params=params).json()
                except Exception:
                    continue

                for hit in data.get("hits", []):
                    title = hit.get("title") or hit.get("story_title") or query
                    body = hit.get("comment_text") or hit.get("story_text") or ""
                    hn_id = hit.get("objectID")
                    created = hit.get("created_at")

                    try:
                        posted_at = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    except Exception:
                        posted_at = datetime.now(timezone.utc)

                    items.append(
                        RawItem(
                            source="hackernews",
                            source_type="social_post",
                            url=f"https://news.ycombinator.com/item?id={hn_id}",
                            title=title,
                            body=body,
                            company="unknown",
                            posted_at=posted_at,
                            location="unknown",
                            remote_text="unknown",
                            salary_text=None,
                            employment_type="unknown",
                        )
                    )

        return items
