from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Opportunity
from .storage_models import OpportunityRecord, ScanRunRecord


class Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_run(self, *, started_at, completed_at, source_count: int, raw_item_count: int, opportunity_count: int, status: str = "completed") -> ScanRunRecord:
        record = ScanRunRecord(
            started_at=started_at,
            completed_at=completed_at,
            source_count=source_count,
            raw_item_count=raw_item_count,
            opportunity_count=opportunity_count,
            status=status,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def upsert_opportunities(self, opportunities: list[Opportunity]) -> None:
        for opp in opportunities:
            payload = opp.model_dump()
            payload["job_url"] = str(payload["job_url"])
            payload["application_url"] = str(payload["application_url"])

            existing = self.db.execute(
                select(OpportunityRecord).where(OpportunityRecord.id == opp.id)
            ).scalar_one_or_none()

            if existing:
                for key, value in payload.items():
                    setattr(existing, key, value)
            else:
                self.db.add(OpportunityRecord(**payload))

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()

    def list_opportunities(self, limit: int = 100) -> list[Opportunity]:
        stmt = select(OpportunityRecord).order_by(
            OpportunityRecord.score.desc(),
            OpportunityRecord.posted_date.desc(),
        ).limit(limit)

        rows = self.db.execute(stmt).scalars().all()

        return [Opportunity.model_validate({
            "id": row.id,
            "date_found": row.date_found,
            "posted_date": row.posted_date,
            "company": row.company,
            "job_title": row.job_title,
            "employment_type": row.employment_type,
            "location": row.location,
            "remote_status": row.remote_status,
            "salary_min_usd": row.salary_min_usd,
            "salary_max_usd": row.salary_max_usd,
            "salary_confidence": row.salary_confidence,
            "source": row.source,
            "source_type": row.source_type,
            "source_category": row.source_category or "lead",
            "signal_type": row.signal_type,
            "job_url": row.job_url,
            "application_url": row.application_url,
            "score": row.score,
            "match_reason": row.match_reason,
            "eligibility_risk": row.eligibility_risk,
            "apply_priority": row.apply_priority,
            "recommended_action": row.recommended_action,
            "status": row.status,
            "notes": row.notes,
        }) for row in rows]

    def recent_runs(self, limit: int = 20) -> list[ScanRunRecord]:
        stmt = select(ScanRunRecord).order_by(ScanRunRecord.completed_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
