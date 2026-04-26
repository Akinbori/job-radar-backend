from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re

from .models import Opportunity, RawItem
from .scoring import OpportunityScorer

SALARY_RE = re.compile(r"\$?(\d{2,3}(?:,\d{3})+|\d{2,3}k)", re.I)

INCLUDE = [
    "content", "content marketing", "content strategy", "content strategist",
    "content lead", "head of content", "seo", "newsletter", "editorial",
    "copywriter", "copywriting", "lifecycle", "email marketing", "crm",
    "retention", "demand gen", "demand generation", "growth marketing",
    "gtm", "go-to-market", "thought leadership", "founder content"
]

EXCLUDE = [
    "engineer", "developer", "software", "frontend", "backend", "data scientist",
    "fp&a", "finance", "accounting", "legal", "counsel", "sales development",
    "sdr", "account executive", "customer support", "content moderator",
    "moderation", "trust and safety", "intern", "video editor"
]


@dataclass(slots=True)
class Pipeline:
    scorer: OpportunityScorer

    def parse_salary(self, salary_text: str | None) -> tuple[int | None, int | None]:
        if not salary_text:
            return None, None
        matches = SALARY_RE.findall(salary_text)
        values = []
        for raw in matches[:2]:
            cleaned = raw.lower().replace(",", "")
            values.append(int(cleaned[:-1]) * 1000 if cleaned.endswith("k") else int(cleaned))
        if not values:
            return None, None
        return (values[0], values[0]) if len(values) == 1 else (min(values), max(values))

    def is_relevant(self, raw: RawItem) -> bool:
        text = f"{raw.title} {raw.body} {raw.location} {raw.remote_text}".lower()

        if any(bad in text for bad in EXCLUDE):
            return False

        return any(good in text for good in INCLUDE)

    def infer_signal_type(self, raw: RawItem) -> str:
        if raw.source_type in {"ats", "job_board"}:
            return "formal_opening"
        text = f"{raw.title} {raw.body}".lower()
        if any(x in text for x in ["looking for", "need a", "hiring", "seeking"]):
            return "informal_hiring_post"
        return "warm_outbound_target"

    def decide_action(self, score: int, signal_type: str) -> tuple[str, str]:
        if score >= 85:
            return "high", "apply_now" if signal_type == "formal_opening" else "send_outreach"
        if score >= 70:
            return "medium", "apply_now" if signal_type == "formal_opening" else "send_outreach"
        return "low", "discard"

    def normalize(self, raw: RawItem) -> Opportunity:
        salary_min, salary_max = self.parse_salary(raw.salary_text)
        breakdown, match_reason, risk, salary_conf = self.scorer.score(raw, salary_min, salary_max)
        signal_type = self.infer_signal_type(raw)
        priority, action = self.decide_action(breakdown.total, signal_type)
        key = f"{raw.company.lower()}::{raw.title.lower()}::{raw.url}"
        opp_id = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

        return Opportunity(
            id=opp_id,
            date_found=datetime.now(timezone.utc),
            posted_date=raw.posted_at,
            company=raw.company,
            job_title=raw.title,
            employment_type=raw.employment_type,
            location=raw.location,
            remote_status=raw.remote_text,
            salary_min_usd=salary_min,
            salary_max_usd=salary_max,
            salary_confidence=salary_conf,
            source=raw.source,
            source_type=raw.source_type,
            signal_type=signal_type,
            job_url=raw.url,
            application_url=raw.url,
            score=breakdown.total,
            match_reason=match_reason,
            eligibility_risk=risk,
            apply_priority=priority,
            recommended_action=action,
            notes="filtered for Bayo profile",
        )

    def dedupe(self, opportunities: list[Opportunity]) -> list[Opportunity]:
        filtered = [opp for opp in opportunities if opp.recommended_action != "discard"]

        seen: dict[tuple[str, str], Opportunity] = {}
        for opp in filtered:
            key = (opp.company.strip().lower(), opp.job_title.strip().lower())
            existing = seen.get(key)
            if existing is None or opp.score > existing.score:
                seen[key] = opp

        return sorted(seen.values(), key=lambda item: item.score, reverse=True)
