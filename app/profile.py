TARGET_ROLES = [
    "lifecycle marketing manager",
    "email marketing manager",
    "crm marketing manager",
    "retention marketing manager",
    "content marketing manager",
    "content strategist",
    "content strategy lead",
    "content lead",
    "head of content",
    "founder content lead",
    "thought leadership lead",
    "newsletter strategist",
    "seo content manager",
    "demand generation manager",
    "growth marketing manager",
    "gtm strategist",
    "growth strategist",
]

INCLUDE_KEYWORDS = [
    "content",
    "content marketing",
    "content strategy",
    "content lead",
    "head of content",
    "founder content",
    "founder-led content",
    "thought leadership",
    "ghostwriting",
    "linkedin",
    "newsletter",
    "editorial",
    "seo content",
    "b2b content",
    "lifecycle",
    "email marketing",
    "crm",
    "retention",
    "demand generation",
    "demand gen",
    "growth marketing",
    "gtm",
    "go-to-market",
    "audience",
    "segmentation",
    "organic growth",
]

EXCLUDE_KEYWORDS = [
    "content moderator",
    "moderation",
    "content reviewer",
    "trust and safety",
    "ugc creator",
    "video editor",
    "social media intern",
    "internship",
    "unpaid",
    "commission only",
    "equity only",
    "onsite",
    "on-site",
    "hybrid",
    "must be based in the us",
    "us only",
    "u.s. only",
    "united states only",
    "uk only",
    "must be based in the uk",
]

REMOTE_POSITIVE_KEYWORDS = [
    "remote",
    "remote worldwide",
    "fully remote",
    "global remote",
    "work from anywhere",
    "anywhere",
    "distributed team",
]

REMOTE_NEGATIVE_KEYWORDS = [
    "hybrid",
    "onsite",
    "on-site",
    "office-based",
    "must be based in",
    "us only",
    "uk only",
]

SALARY_MIN_USD = 36000
SALARY_TARGET_MIN_USD = 50000
SALARY_TARGET_MAX_USD = 80000

KEEP_HIGHER_THAN_TARGET = True
ALLOW_MISSING_SALARY_IF_STRONG_FIT = True

FRESHNESS_DAYS = 3

LOCATION_RULES = {
    "fully_remote_only": True,
    "allow_worldwide": True,
    "allow_nigeria": True,
    "reject_us_only": True,
    "reject_uk_only": True,
    "reject_geo_locked": True,
}

PROFILE_SUMMARY = """
Bayo is a B2B content and growth marketer focused on lifecycle/email,
content marketing, demand generation, founder-led growth, thought leadership,
organic acquisition, newsletters, segmentation, and GTM copywriting.

Prioritize remote roles that fit these strengths, including both formal job
posts and informal hiring signals where someone is looking for content,
email, lifecycle, growth, or founder-led marketing help.
"""
