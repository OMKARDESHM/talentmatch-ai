import re
from dataclasses import dataclass, field


SKILL_ALIASES = {
    "python": ("python",),
    "fastapi": ("fastapi", "fast api"),
    "flask": ("flask",),
    "django": ("django",),
    "java": ("java",),
    "spring boot": ("spring boot", "springboot"),
    "javascript": ("javascript", "js"),
    "typescript": ("typescript",),
    "react": ("react", "reactjs", "react.js"),
    "sql": ("sql",),
    "postgresql": ("postgresql", "postgres"),
    "mysql": ("mysql",),
    "tableau": ("tableau",),
    "pytorch": ("pytorch", "torch"),
    "machine learning": ("machine learning", "ml"),
}

ROLE_ALIASES = {
    "backend": (
        "backend",
        "back end",
        "back-end",
        "api developer",
        "api engineer",
    ),
    "frontend": (
        "frontend",
        "front end",
        "front-end",
        "ui developer",
    ),
    "data analyst": (
        "data analyst",
        "analytics",
        "analyst",
    ),
    "machine learning": (
        "machine learning",
        "ml engineer",
        "ml role",
    ),
}

DOMAIN_ALIASES = {
    "healthcare": (
        "healthcare",
        "health care",
        "healthtech",
        "health tech",
        "medical",
    ),
    "fintech": (
        "fintech",
        "financial technology",
        "finance",
        "banking",
    ),
    "e-commerce": (
        "e-commerce",
        "ecommerce",
        "online retail",
    ),
}

EXPERIENCE_ALIASES = {
    "entry level": (
        "entry level",
        "entry-level",
        "fresher",
        "fresh graduate",
        "graduate role",
        "junior",
    ),
    "mid level": (
        "mid level",
        "mid-level",
        "intermediate",
    ),
    "senior": (
        "senior",
        "lead",
    ),
}

LOCATION_ALIASES = {
    "pune": ("pune",),
    "mumbai": ("mumbai",),
    "bengaluru": (
        "bengaluru",
        "bangalore",
    ),
    "remote": (
        "remote",
        "work from home",
        "wfh",
    ),
}


@dataclass(frozen=True)
class MatchingIntent:
    skills: list[str] = field(default_factory=list)
    role_types: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    experience_levels: list[str] = field(default_factory=list)


def normalize_text(value: str) -> str:
    normalized = value.lower()
    normalized = re.sub(r"[^a-z0-9+#.\-\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def contains_alias(text: str, alias: str) -> bool:
    pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

    return re.search(pattern, text) is not None


def extract_matches(
    text: str,
    aliases: dict[str, tuple[str, ...]],
) -> list[str]:
    matches = []

    for canonical_value, alias_values in aliases.items():
        if any(
            contains_alias(text, alias)
            for alias in alias_values
        ):
            matches.append(canonical_value)

    return matches


def parse_matching_intent(query: str) -> MatchingIntent:
    normalized_query = normalize_text(query)

    return MatchingIntent(
        skills=extract_matches(
            normalized_query,
            SKILL_ALIASES,
        ),
        role_types=extract_matches(
            normalized_query,
            ROLE_ALIASES,
        ),
        domains=extract_matches(
            normalized_query,
            DOMAIN_ALIASES,
        ),
        locations=extract_matches(
            normalized_query,
            LOCATION_ALIASES,
        ),
        experience_levels=extract_matches(
            normalized_query,
            EXPERIENCE_ALIASES,
        ),
    )