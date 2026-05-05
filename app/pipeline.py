from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import html
import re

from .models import Opportunity, RawItem
from .scoring import OpportunityScorer


SALARY_RE = re.compile(r"\$?(\d{2,3}(?:,\d{3})+|\d{2,3}k)", re.I)

INCLUDE_KEYWORDS = [
    "content marketing",
    "content marketer",
    "content manager",
    "marketing manager",
    "growth marketing",
    "growth marketer",
    "lifecycle marketing",
    "email marketing",
    "crm marketing",
    "demand generation",
    "demand gen",
    "b2b marketing",
    "saas marketing",
    "newsletter marketing",
]

EXCLUDE_KEYWORDS = [
    "ugc",
    "creator",
    "influencer",
    "community",
    "enablement",
    "program manager",
    "education",
    "learning",
    "evangelist",
    "content moderator",
    "video editor",
    "engineer",
    "developer",
    "legal",
    "accounting",
    "sdr",
    "sales development",
]


@dataclass(slots=True)
class Pipeline:
    scorer: OpportunityScorer

    def clean_title(self, title: str | None) -> str:
        if not title:
            return "Untitled role"

        text = html.unescape(title)
        text = re.sub(r"(?i)\[?hiring\]?", "", text)
        text = re.sub(r"(?i)\bwe'?re hiring\b", "", text)
        text = re.sub(r"(?i)\bwe are hiring\b", "", text)
        text = re.sub(r"[📢🚨🔥✅⭐️]", "", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip(" -|:").strip()

    def parse_salary(self, salary_text: str | None) -> tuple[int | None, int | None]:
        if not salary_text:
            return None, None

        matches = SALARY_RE.findall(salary_text)
        values = []

        for raw in matches[:2]:
            cleaned = raw.lower().replace(",", "")
            values.append(
                int(cleaned[:-1]) * 1000 if cleaned.endswith("k") else int(cleaned)
            )

        if not values:
            return None, None

        return (values[0], values[0]) if len(values) == 1 else (min(values), max(values))

    def infer_signal_type(self, raw: RawItem) -> str:
        if raw.source_type in {"ats", "job_board"}:
            return "formal_opening"

        text = f"{raw.title} {raw.body}".lower()

        if any(x in text for x in ["looking for", "need a", "hiring", "seeking", "dm me", "apply here"]):
            return "informal_hiring_post"

        return "warm_outbound_target"

    def is_relevant(self, opp: Opportunity) -> bool:
        title_text = opp.job_title.lower()
        full_text = f"{opp.job_title} {opp.company} {opp.location} {opp.remote_status} {opp.notes}".lower()

        if any(x in title_text for x in EXCLUDE_KEYWORDS):
            return False

        if not any(k in full_text for k in INCLUDE_KEYWORDS):
            return False

        if opp.salary_min_usd is not None and opp.salary_min_usd < 36000:
            return False

        return True

    def decide_action(self, score: int, signal_type: str) -> tuple[str, str]:
        if score >= 85:
            return "high", "apply_now" if signal_type == "formal_opening" else "send_outreach"

        if score >= 70:
            return "medium", "apply_now" if signal_type == "formal_opening" else "send_outreach"

        return "low", "monitor"

    def normalize(self, raw: RawItem) -> Opportunity:
        salary_min, salary_max = self.parse_salary(raw.salary_text)
        breakdown, match_reason, risk, salary_conf = self.scorer.score(
            raw, salary_min, salary_max
        )
        signal_type = self.infer_signal_type(raw)
        priority, action = self.decide_action(breakdown.total, signal_type)

        clean_job_title = self.clean_title(raw.title)
        company = raw.company or "unknown"

        key = f"{company.lower()}::{clean_job_title.lower()}::{raw.url}::{raw.source}"
        opp_id = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

        notes = raw.body[:2000] if raw.body else "generated from MVP pipeline"

        return Opportunity(
            id=opp_id,
            date_found=datetime.now(timezone.utc),
            posted_date=raw.posted_at or raw.date_found or datetime.now(timezone.utc),
            company=company,
            job_title=clean_job_title,
            employment_type=raw.employment_type,
            location=raw.location,
            remote_status=raw.remote_text,
            salary_min_usd=salary_min,
            salary_max_usd=salary_max,
            salary_confidence=salary_conf,
            source=raw.source,
            source_type=raw.source_type,
            source_category="verified" if raw.source_type in {"ats", "job_board"} else "lead",
            signal_type=signal_type,
            job_url=raw.url,
            application_url=raw.url,
            score=breakdown.total,
            match_reason=match_reason,
            eligibility_risk=risk,
            apply_priority=priority,
            recommended_action=action,
            notes=notes,
        )

    def dedupe(self, opportunities: list[Opportunity]) -> list[Opportunity]:
        seen = {}

        for opp in opportunities:
            if not self.is_relevant(opp):
                continue

            key = (
                opp.company.strip().lower(),
                opp.job_title.strip().lower(),
                str(opp.job_url).strip().lower(),
            )

            existing = seen.get(key)

            if existing is None or opp.score > existing.score:
                seen[key] = opp

        return sorted(seen.values(), key=lambda item: item.score, reverse=True)
