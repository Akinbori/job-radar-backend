from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


SourceType = Literal[
    "ats",
    "job_board",
    "social_post",
    "portfolio_page",
    "community",
    "manual",
]

SignalType = Literal[
    "formal_opening",
    "informal_hiring_post",
    "portfolio_lead",
    "warm_outbound_target",
]

SourceCategory = Literal["verified", "lead"]

ActionType = Literal["apply_now", "send_outreach", "monitor", "discard"]
PriorityType = Literal["high", "medium", "low"]
SalaryConfidence = Literal["high", "medium", "low", "unknown"]
StatusType = Literal["new", "reviewed", "applied", "contacted", "discarded"]


class RawItem(BaseModel):
    source: str
    source_type: SourceType
    url: HttpUrl
    title: str
    body: str = ""
    company: str = "unknown"
    author: Optional[str] = None
    posted_at: datetime
    location: str = "unknown"
    remote_text: str = "unknown"
    salary_text: Optional[str] = None
    employment_type: str = "unknown"


class Opportunity(BaseModel):
    id: str
    date_found: datetime
    posted_date: datetime
    company: str
    job_title: str
    employment_type: str
    location: str
    remote_status: str
    salary_min_usd: Optional[int] = None
    salary_max_usd: Optional[int] = None
    salary_confidence: SalaryConfidence = "unknown"
    source: str
    source_type: SourceType
    source_category: SourceCategory = "lead"
    signal_type: SignalType
    job_url: HttpUrl
    application_url: HttpUrl
    score: int = Field(ge=0, le=100)
    match_reason: str
    eligibility_risk: str
    apply_priority: PriorityType
    recommended_action: ActionType
    status: StatusType = "new"
    notes: str = ""


class ScanResponse(BaseModel):
    run_timestamp: datetime
    opportunity_count: int
    opportunities: list[Opportunity]


class ScanRunSummary(BaseModel):
    id: int
    started_at: datetime
    completed_at: datetime
    source_count: int
    raw_item_count: int
    opportunity_count: int
    status: str


class DashboardResponse(BaseModel):
    run_timestamp: datetime
    latest_run: ScanRunSummary | None = None
    runs: list[ScanRunSummary]
    opportunities: list[Opportunity]
