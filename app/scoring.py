from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .models import RawItem
from .profile import PROFILE, SearchProfile


@dataclass(slots=True)
class ScoreBreakdown:
    functional_fit: int
    remote_geo: int
    compensation: int
    recency: int
    conversion_velocity: int

    @property
    def total(self) -> int:
        return self.functional_fit + self.remote_geo + self.compensation + self.recency + self.conversion_velocity


class OpportunityScorer:
    def __init__(self, profile: SearchProfile = PROFILE) -> None:
        self.profile = profile

    def _functional_fit(self, text: str) -> int:
        text_l = text.lower()
        hits = sum(1 for kw in self.profile.functional_keywords if kw in text_l)
        if hits >= 5:
            return 35
        if hits >= 3:
            return 28
        if hits >= 2:
            return 22
        if hits >= 1:
            return 14
        return 0

    def _remote_geo(self, remote_text: str, location: str) -> tuple[int, str]:
        combined = f"{remote_text} {location}".lower()
        if any(term in combined for term in self.profile.excluded_geo_terms):
            return 0, "likely geo-restricted"
        if "worldwide" in combined or "global" in combined:
            return 25, "none visible"
        if "remote" in combined:
            return 20, "remote wording ambiguous"
        return 0, "not fully remote"

    def _compensation(self, salary_min: Optional[int], salary_max: Optional[int]) -> tuple[int, str]:
        if salary_min is None and salary_max is None:
            return (10 if PROFILE.preferred_salary_min_usd else 0), "low"
        floor = self.profile.preferred_salary_min_usd
        ceil = self.profile.preferred_salary_max_usd
        lower = salary_min if salary_min is not None else salary_max or 0
        upper = salary_max if salary_max is not None else salary_min or 0
        if upper >= floor and lower <= ceil:
            return 20, "high"
        if upper > ceil:
            return 18, "high"
        if upper >= int(floor * 0.8):
            return 10, "medium"
        return 0, "high"

    def _recency(self, posted_at: datetime) -> int:
        now = datetime.now(timezone.utc)
        delta_days = (now - posted_at.astimezone(timezone.utc)).days
        if delta_days <= 0:
            return 10
        if delta_days == 1:
            return 8
        if delta_days == 2:
            return 6
        if delta_days == 3:
            return 4
        return 0

    def _conversion_velocity(self, raw: RawItem) -> int:
        text = f"{raw.title} {raw.body}".lower()
        if raw.source_type == "ats":
            return 10
        if any(phrase in text for phrase in ["looking for", "need a", "hiring", "seeking"]):
            return 8
        return 5

    def score(self, raw: RawItem, salary_min: Optional[int], salary_max: Optional[int]) -> tuple[ScoreBreakdown, str, str, str]:
        functional = self._functional_fit(f"{raw.title} {raw.body}")
        remote_geo, risk = self._remote_geo(raw.remote_text, raw.location)
        compensation, salary_conf = self._compensation(salary_min, salary_max)
        recency = self._recency(raw.posted_at)
        velocity = self._conversion_velocity(raw)
        breakdown = ScoreBreakdown(functional, remote_geo, compensation, recency, velocity)
        reason_bits = []
        if functional >= 28:
            reason_bits.append("strong functional fit")
        elif functional >= 14:
            reason_bits.append("partial functional fit")
        if remote_geo >= 20:
            reason_bits.append("remote looks viable")
        if compensation >= 18:
            reason_bits.append("compensation aligned")
        elif compensation > 0 and salary_conf == "low":
            reason_bits.append("salary not listed but plausible")
        if recency >= 8:
            reason_bits.append("fresh posting")
        if velocity >= 8:
            reason_bits.append("fast conversion path")
        return breakdown, ", ".join(reason_bits) or "needs manual review", risk, salary_conf
