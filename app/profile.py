from dataclasses import dataclass, field


@dataclass(slots=True)
class SearchProfile:
    candidate_name: str = "Bayo Hassan Adesokan"
    email: str = "bayo.adesokan9@gmail.com"
    target_roles: list[str] = field(
        default_factory=lambda: [
            "Lifecycle/Email Marketing Manager",
            "Content Marketing Manager",
            "Demand Gen Manager",
            "GTM / Growth Strategist",
            "Growth Marketing Manager",
            "Founder-led growth / thought leadership",
        ]
    )
    must_be_fully_remote: bool = True
    base_location: str = "Nigeria"
    excluded_geo_terms: list[str] = field(
        default_factory=lambda: [
            "us only",
            "united states only",
            "uk only",
            "must be based in uk",
            "must be based in us",
            "canada only",
            "europe only",
            "eu only",
        ]
    )
    preferred_salary_min_usd: int = 36000
    preferred_salary_max_usd: int = 60000
    accepted_employment_types: list[str] = field(
        default_factory=lambda: ["full-time", "contract", "freelance", "fractional", "part-time"]
    )
    functional_keywords: list[str] = field(
        default_factory=lambda: [
            "lifecycle",
            "email",
            "crm",
            "retention",
            "content marketing",
            "content strategist",
            "demand gen",
            "growth strategist",
            "thought leadership",
            "ghostwriting",
            "founder-led growth",
            "newsletter",
            "segmentation",
            "organic acquisition",
        ]
    )
    evidence_points: list[str] = field(
        default_factory=lambda: [
            "Improved email open rates from 40-50% to 65% at Wonsulting",
            "Helped the team reach its first USD 200k monthly revenue milestone",
            "Built an email campaign that generated USD 10k revenue and 54 sales calls",
            "Segmented a 1.2M email list by audience needs",
            "Built a Reddit acquisition strategy that cut costs and generated organic clients",
            "Took a B2B founder from invisible to 80k LinkedIn impressions",
            "Generated an inbound lead that resulted in a USD 20k contract",
        ]
    )


PROFILE = SearchProfile()
