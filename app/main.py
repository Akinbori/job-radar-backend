
from __future__ import annotations

from datetime import datetime, timezone
import csv
import io

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db, run_migrations
from .models import DashboardResponse, ScanResponse, ScanRunSummary
from .repository import Repository
from .services import RadarService


Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, 
                   "http://localhost:3000", 
                   "http://127.0.0.1:3000", 
                   "https://job-radar-frontend-hisyskgkc-akinboris-projects.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = RadarService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@app.post("/scan", response_model=ScanResponse)
def run_scan(db: Session = Depends(get_db)) -> ScanResponse:
    repo = Repository(db)
    opportunities, _ = service.run_scan(repo)
    return ScanResponse(
        run_timestamp=datetime.now(timezone.utc),
        opportunity_count=len(opportunities),
        opportunities=opportunities,
    )


@app.get("/opportunities", response_model=list)
def opportunities(db: Session = Depends(get_db)):
    return Repository(db).list_opportunities()


@app.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    repo = Repository(db)
    runs = [
        ScanRunSummary(
            id=row.id,
            started_at=row.started_at,
            completed_at=row.completed_at,
            source_count=row.source_count,
            raw_item_count=row.raw_item_count,
            opportunity_count=row.opportunity_count,
            status=row.status,
        )
        for row in repo.recent_runs()
    ]
    latest_run = runs[0] if runs else None
    return DashboardResponse(
        run_timestamp=datetime.now(timezone.utc),
        latest_run=latest_run,
        runs=runs,
        opportunities=repo.list_opportunities(),
    )


@app.get("/tracker.csv", response_class=PlainTextResponse)
def tracker_csv(db: Session = Depends(get_db)) -> str:
    opportunities = Repository(db).list_opportunities(limit=1000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "date_found","posted_date","company","job_title","employment_type","location","remote_status",
        "salary_min_usd","salary_max_usd","salary_confidence","source","source_type","job_url",
        "application_url","match_score","match_reason","eligibility_risk","apply_priority","status","notes"
    ])
    for opp in opportunities:
        writer.writerow([
            opp.date_found.date().isoformat(),
            opp.posted_date.date().isoformat(),
            opp.company,
            opp.job_title,
            opp.employment_type,
            opp.location,
            opp.remote_status,
            opp.salary_min_usd or "unknown",
            opp.salary_max_usd or "unknown",
            opp.salary_confidence,
            opp.source,
            opp.source_type,
            str(opp.job_url),
            str(opp.application_url),
            opp.score,
            opp.match_reason,
            opp.eligibility_risk,
            opp.apply_priority,
            opp.status,
            opp.notes,
        ])
    return output.getvalue()
