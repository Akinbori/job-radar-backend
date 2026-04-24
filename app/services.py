from __future__ import annotations

from datetime import datetime, timezone

from .adapters.live_sources import GreenhouseBoardAdapter, LeverPostingsAdapter
from .adapters.sample_data import SampleStructuredAdapter, SampleUnstructuredAdapter
from .models import Opportunity, ScanRunSummary
from .pipeline import Pipeline
from .repository import Repository
from .scoring import OpportunityScorer


class RadarService:
    def __init__(self) -> None:
        self.pipeline = Pipeline(scorer=OpportunityScorer())
        self.adapters = [
            SampleStructuredAdapter(),
            SampleUnstructuredAdapter(),
            GreenhouseBoardAdapter(),
            LeverPostingsAdapter(),
        ]

    def run_scan(self, repo: Repository) -> tuple[list[Opportunity], ScanRunSummary]:
        started_at = datetime.now(timezone.utc)
        normalized: list[Opportunity] = []
        raw_count = 0
        active_adapters = 0
        for adapter in self.adapters:
            raw_items = adapter.fetch()
            if not raw_items:
                continue
            active_adapters += 1
            raw_count += len(raw_items)
            normalized.extend(self.pipeline.normalize(raw) for raw in raw_items)
        opportunities = self.pipeline.dedupe(normalized)
        repo.upsert_opportunities(opportunities)
        run = repo.save_run(
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            source_count=active_adapters,
            raw_item_count=raw_count,
            opportunity_count=len(opportunities),
        )
        return opportunities, ScanRunSummary(
            id=run.id,
            started_at=run.started_at,
            completed_at=run.completed_at,
            source_count=run.source_count,
            raw_item_count=run.raw_item_count,
            opportunity_count=run.opportunity_count,
            status=run.status,
        )
