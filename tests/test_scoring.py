from datetime import datetime, timedelta, timezone

from app.models import RawItem
from app.pipeline import Pipeline
from app.scoring import OpportunityScorer


def test_formal_role_scores_high_and_applies():
    raw = RawItem(
        source="greenhouse",
        source_type="ats",
        url="https://example.com/role",
        title="Lifecycle Marketing Manager",
        body="Own email, CRM, newsletter, segmentation, retention, and content systems.",
        company="ExampleCo",
        posted_at=datetime.now(timezone.utc) - timedelta(hours=2),
        location="Remote worldwide",
        remote_text="Fully remote global",
        salary_text="$45k - $60k",
        employment_type="full-time",
    )
    opp = Pipeline(OpportunityScorer()).normalize(raw)
    assert opp.score >= 85
    assert opp.recommended_action == "apply_now"


def test_informal_role_routes_to_outreach():
    raw = RawItem(
        source="reddit",
        source_type="social_post",
        url="https://example.com/post",
        title="Looking for a content marketer",
        body="Need lifecycle emails, newsletters, and founder LinkedIn posts.",
        company="unknown",
        posted_at=datetime.now(timezone.utc) - timedelta(hours=4),
        location="Remote",
        remote_text="Remote async",
        salary_text=None,
        employment_type="fractional",
    )
    opp = Pipeline(OpportunityScorer()).normalize(raw)
    assert opp.recommended_action == "send_outreach"
