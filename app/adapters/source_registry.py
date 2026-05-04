import os

from .live_sources import GreenhouseBoardAdapter, LeverPostingsAdapter
from .workable_sources import WorkablePublicJobsAdapter
from .ashby_sources import AshbyJobsAdapter
from .social_sources import RedditHiringSignalAdapter, HackerNewsHiringSignalAdapter
from .search_sources import SerpApiHiringSignalAdapter


DEFAULT_GREENHOUSE_BOARDS = [
    "klaviyo",
    "hubspot",
    "braze",
    "customerio",
    "activecampaign",
    "buffer",
]

DEFAULT_LEVER_COMPANIES = [
    "apollo",
    "gong",
    "clearbit",
    "ashbyhq",
]

DEFAULT_WORKABLE_COMPANIES = [
    "pavago",
]

DEFAULT_ASHBY_COMPANIES = [
    "ashby",
    "levels.fyi",
]


def _split_env(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def build_default_adapters():
    greenhouse_boards = _split_env("GREENHOUSE_BOARD_TOKENS") or DEFAULT_GREENHOUSE_BOARDS
    lever_companies = _split_env("LEVER_COMPANIES") or DEFAULT_LEVER_COMPANIES
    workable_companies = _split_env("WORKABLE_COMPANIES") or DEFAULT_WORKABLE_COMPANIES
    ashby_companies = _split_env("ASHBY_COMPANIES") or DEFAULT_ASHBY_COMPANIES

    adapters = []

    for board in greenhouse_boards:
        adapters.append(GreenhouseBoardAdapter(board_token=board))

    for company in lever_companies:
        adapters.append(LeverPostingsAdapter(company_handle=company))

    for company in workable_companies:
        adapters.append(WorkablePublicJobsAdapter(subdomain=company))

    for company in ashby_companies:
        adapters.append(AshbyJobsAdapter(company=company))

    adapters.append(RedditHiringSignalAdapter())
    adapters.append(HackerNewsHiringSignalAdapter())
    adapters.append(SerpApiHiringSignalAdapter())

    return adapters
