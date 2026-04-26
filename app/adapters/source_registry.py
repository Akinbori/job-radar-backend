import os

from .live_sources import GreenhouseBoardAdapter, LeverPostingsAdapter
from .social_sources import RedditHiringSignalAdapter, HackerNewsHiringSignalAdapter
from .search_sources import SerpApiHiringSignalAdapter


DEFAULT_GREENHOUSE_BOARDS = [
    "gitlab",
    "webflow",
    "calendly",
    "deel",
    "remote",
    "hotjar",
    "typeform",
    "mural",
    "miro",
    "posthog",
    "airtable",
    "klaviyo",
    "customerio",
    "helpscout",
    "activecampaign",
    "braze",
    "typeform",
    "hubspot",
    "buffer",
]

DEFAULT_LEVER_COMPANIES = [
    "shopify",
    "remote",
    "doist",
    "supabase",
    "linear",
    "vercel",
    "loom",
    "pilot",
    "ashbyhq",
    "gong",
    "apollo",
    "clearbit",
    "webflow",
]


def _split_env(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def build_default_adapters():
    greenhouse_boards = _split_env("GREENHOUSE_BOARD_TOKENS") or DEFAULT_GREENHOUSE_BOARDS
    lever_companies = _split_env("LEVER_COMPANIES") or DEFAULT_LEVER_COMPANIES

    adapters = []

    for board in greenhouse_boards:
        adapters.append(GreenhouseBoardAdapter(board_token=board))

    for company in lever_companies:
        adapters.append(LeverPostingsAdapter(company_handle=company))

    adapters.append(RedditHiringSignalAdapter())
    adapters.append(HackerNewsHiringSignalAdapter())
    adapters.append(SerpApiHiringSignalAdapter())

    return adapters
