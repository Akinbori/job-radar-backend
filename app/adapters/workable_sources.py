from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.models import RawItem


class WorkablePublicJobsAdapter:
    name = "workable"

    def __init__(self, subdomain: str) -> None:
        self.subdomain = subdomain

    def fetch(self) -> list[RawItem]:
        url = f"https://www.workable.com/api/accounts/{self.subdomain}?details=true"

        with httpx.Client(timeout=20.0) as client:
            res = client.get(url)
            if res.status_code != 200:
                return []
            data = res.json()

        jobs = data.get("jobs", data if isinstance(data, list) else [])
        items: list[RawItem] = []

        for job in jobs:
            title = job.get("title") or job.get("full_title")
            job_url = job.get("url") or job.get("shortlink")

            if not title or not job_url:
                continue

            location_data: Any = job.get("location") or {}
            location = (
                location_data.get("location_str")
                or location_data.get("city")
                or job.get("location")
                or "unknown"
            )

            posted_at = job.get("published") or job.get("created_at") or job.get("updated_at")

            try:
                posted_date = datetime.fromisoformat(str(posted_at).replace("Z", "+00:00"))
            except Exception:
                posted_date = datetime.now(timezone.utc)

            items.append(
                RawItem(
                    source="workable",
                    source_type="ats",
                    url=job_url,
                    title=title,
                    body=(job.get("description") or "")[:4000],
                    company=data.get("name", self.subdomain),
                    posted_at=posted_date,
                    location=str(location),
                    remote_text=str(location),
                    salary_text=None,
                    employment_type=job.get("type") or "unknown",
                )
            )

        return items
