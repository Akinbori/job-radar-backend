from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any

import httpx

from app.models import RawItem


class GreenhouseBoardAdapter:
    name = "greenhouse"

    def __init__(self, board_token: str | None = None) -> None:
        self.board_token = board_token or os.getenv("GREENHOUSE_BOARD_TOKEN")

    def fetch(self) -> list[RawItem]:
        if not self.board_token:
            return []
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs"
        with httpx.Client(timeout=20.0) as client:
            data = client.get(url).json()
        items: list[RawItem] = []
        for job in data.get("jobs", []):
            updated = datetime.fromisoformat(job.get("updated_at", datetime.now(timezone.utc).isoformat()).replace("Z", "+00:00"))
            location = (job.get("location") or {}).get("name") or "unknown"
            items.append(
                RawItem(
                    source="greenhouse",
                    source_type="ats",
                    url=job["absolute_url"],
                    title=job["title"],
                    body=job.get("content", "")[:4000],
                    company=data.get("company_name", self.board_token),
                    posted_at=updated,
                    location=location,
                    remote_text=location,
                    salary_text=None,
                    employment_type="full-time",
                )
            )
        return items


class LeverPostingsAdapter:
    name = "lever"

    def __init__(self, company_handle: str | None = None) -> None:
        self.company_handle = company_handle or os.getenv("LEVER_COMPANY_HANDLE")

    def fetch(self) -> list[RawItem]:
        if not self.company_handle:
            return []
        url = f"https://api.lever.co/v0/postings/{self.company_handle}?mode=json"
        with httpx.Client(timeout=20.0) as client:
            data = client.get(url).json()
        items: list[RawItem] = []
        for job in data:
            categories: dict[str, Any] = job.get("categories", {}) or {}
            location = categories.get("location", "unknown")
            commitment = categories.get("commitment", "unknown")
            items.append(
                RawItem(
                    source="lever",
                    source_type="ats",
                    url=job["hostedUrl"],
                    title=job["text"],
                    body=job.get("descriptionPlain", "")[:4000],
                    company=self.company_handle,
                    posted_at=datetime.fromtimestamp(job.get("createdAt", 0) / 1000, tz=timezone.utc),
                    location=location,
                    remote_text=location,
                    salary_text=None,
                    employment_type=commitment.lower() if commitment else "unknown",
                )
            )
        return items
