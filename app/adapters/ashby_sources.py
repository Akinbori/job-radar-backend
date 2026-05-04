from __future__ import annotations

from datetime import datetime, timezone
import httpx

from app.models import RawItem


class AshbyJobsAdapter:
    name = "ashby"

    def __init__(self, company: str) -> None:
        self.company = company

    def fetch(self) -> list[RawItem]:
        url = f"https://jobs.ashbyhq.com/{self.company}"

        items: list[RawItem] = []

        with httpx.Client(timeout=20.0) as client:
            try:
                res = client.get(url)
                if res.status_code != 200:
                    return []
                html = res.text
            except Exception:
                return []

        # crude parse (Ashby doesn’t expose a simple JSON endpoint)
        import re

        matches = re.findall(r'href="(/[^"]+)"[^>]*>([^<]+)</a>', html)

        for link, title in matches:
            if "job" not in link.lower():
                continue

            items.append(
                RawItem(
                    source="ashby",
                    source_type="ats",
                    url=f"https://jobs.ashbyhq.com{link}",
                    title=title.strip(),
                    body="",
                    company=self.company,
                    posted_at=datetime.now(timezone.utc),
                    location="unknown",
                    remote_text="unknown",
                    salary_text=None,
                    employment_type="unknown",
                )
            )

        return items
