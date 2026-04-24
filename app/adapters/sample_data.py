from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models import RawItem


class SampleStructuredAdapter:
    name = "sample_structured"

    def fetch(self) -> list[RawItem]:
        now = datetime.now(timezone.utc)
        return [
            RawItem(
                source="greenhouse",
                source_type="ats",
                url="https://example.com/jobs/lifecycle-marketing-manager",
                title="Lifecycle Marketing Manager",
                body="Own email automation, segmentation, newsletter strategy, CRM campaigns, and retention experiments.",
                company="Northstar SaaS",
                posted_at=now - timedelta(hours=6),
                location="Remote worldwide",
                remote_text="Fully remote, global",
                salary_text="$45,000 - $60,000",
                employment_type="full-time",
            ),
            RawItem(
                source="ashby",
                source_type="ats",
                url="https://example.com/jobs/content-demand-gen-manager",
                title="Content & Demand Gen Manager",
                body="Run B2B SaaS content systems, LinkedIn thought leadership, lifecycle nurture, and founder-led distribution.",
                company="Signal Foundry",
                posted_at=now - timedelta(days=1),
                location="Remote",
                remote_text="Remote across multiple regions",
                salary_text="$55k - $75k",
                employment_type="contract",
            ),
        ]


class SampleUnstructuredAdapter:
    name = "sample_unstructured"

    def fetch(self) -> list[RawItem]:
        now = datetime.now(timezone.utc)
        return [
            RawItem(
                source="reddit",
                source_type="social_post",
                url="https://example.com/r/startups/post/123",
                title="Looking for a B2B SaaS content marketer",
                body="Need someone part-time to turn founder ideas into newsletter, LinkedIn content, and lifecycle emails for a devtools startup.",
                company="unknown",
                author="founder_devtools",
                posted_at=now - timedelta(hours=10),
                location="Remote",
                remote_text="Remote; async friendly",
                salary_text=None,
                employment_type="fractional",
            )
        ]
