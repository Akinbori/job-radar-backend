from dataclasses import dataclass, field

@dataclass(slots=True)
class SearchProfile:
    candidate_name: str = "Bayo Hassan Adesokan"
    email: str = "bayo.adesokan9@gmail.com"
    preferred_salary_min_usd: int = 36000
    preferred_salary_max_usd: int = 80000
    must_be_fully_remote: bool = True
    base_location: str = "Nigeria"

    target_roles: list[str] = field(default_factory=lambda: [
        "Lifecycle/Email Marketing Manager", "Email Marketing Manager",
        "Content Marketing Manager", "Content Strategist", "Content Lead",
        "Head of Content", "Founder Content Lead", "Thought Leadership Lead",
        "Newsletter Strategist", "SEO Content Manager", "Demand Gen Manager",
        "Growth Marketing Manager", "GTM Strategist"
    ])

    functional_keywords: list[str] = field(default_factory=lambda: [
        "content", "content marketing", "content strategy", "founder content",
        "thought leadership", "newsletter", "editorial", "seo content",
        "lifecycle", "email marketing", "crm", "retention", "demand gen",
        "growth marketing", "gtm", "segmentation", "organic growth"
    ])

    excluded_geo_terms: list[str] = field(default_factory=lambda: [
        "us only", "united states only", "u.s. only", "uk only",
        "must be based in uk", "must be based in us", "canada only",
        "europe only", "eu only", "hybrid", "onsite", "on-site"
    ])

    accepted_employment_types: list[str] = field(default_factory=lambda: [
        "full-time", "contract", "freelance", "fractional", "part-time"
    ])

    evidence_points: list[str] = field(default_factory=lambda: [
        "Improved email open rates from 40-50% to 65%",
        "Built email campaign that generated USD 10k and 54 sales calls",
        "Segmented a 1.2M email list",
        "Built Reddit acquisition strategy that generated organic clients",
        "Took B2B founder to 80k LinkedIn impressions",
        "Generated inbound lead that became a USD 20k contract"
    ])

PROFILE = SearchProfile()
