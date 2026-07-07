from dataclasses import dataclass

from app.matching.intent_parser import (
    MatchingIntent,
    normalize_text,
)
from app.models import CandidateProfile, Job


SKILL_WEIGHT = 40.0
ROLE_WEIGHT = 25.0
DOMAIN_WEIGHT = 20.0
LOCATION_WEIGHT = 10.0
EXPERIENCE_WEIGHT = 5.0


@dataclass(frozen=True)
class RankingContext:
    skills: list[str]
    role_types: list[str]
    domains: list[str]
    locations: list[str]
    experience_levels: list[str]


@dataclass(frozen=True)
class RankedJob:
    job: Job
    match_score: int
    explanation: str
    matched_factors: list[str]


def split_values(value: str | None) -> list[str]:
    if not value:
        return []

    return [
        normalize_text(item)
        for item in value.split(",")
        if item.strip()
    ]


def unique_values(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def build_ranking_context(
    intent: MatchingIntent,
    profile: CandidateProfile,
) -> RankingContext:
    query_skills = intent.skills
    profile_skills = split_values(profile.skills)

    skills = unique_values(
        query_skills or profile_skills
    )
    role_types = unique_values(
        intent.role_types
        or split_values(profile.preferred_role_type)
    )
    domains = unique_values(
        intent.domains
        or split_values(profile.domain_interest)
    )
    locations = unique_values(
        intent.locations
        or split_values(profile.preferred_location)
    )

    return RankingContext(
        skills=skills,
        role_types=role_types,
        domains=domains,
        locations=locations,
        experience_levels=intent.experience_levels,
    )


def calculate_overlap_score(
    desired_values: list[str],
    actual_values: list[str],
    weight: float,
) -> tuple[float, list[str]]:
    if not desired_values:
        return 0.0, []

    matched_values = [
        desired
        for desired in desired_values
        if any(
            desired == actual
            or desired in actual
            or actual in desired
            for actual in actual_values
        )
    ]

    if not matched_values:
        return 0.0, []

    score = weight * (
        len(matched_values) / len(desired_values)
    )

    return score, matched_values


def format_factor(label: str, value: str) -> str:
    return f"{label}: {value.title()}"


def build_explanation(
    matched_factors: list[str],
) -> str:
    if not matched_factors:
        return (
            "Limited direct overlap was found, but the role is "
            "included as an available open opportunity."
        )

    if len(matched_factors) == 1:
        return (
            "This role matches your request based on "
            f"{matched_factors[0].lower()}."
        )

    factor_text = ", ".join(
        factor.lower()
        for factor in matched_factors[:-1]
    )

    return (
        "This role matches your request based on "
        f"{factor_text}, and "
        f"{matched_factors[-1].lower()}."
    )


def rank_job(
    job: Job,
    context: RankingContext,
) -> RankedJob:
    score = 0.0
    matched_factors = []

    job_skills = split_values(job.required_skills)

    skill_score, matched_skills = calculate_overlap_score(
        context.skills,
        job_skills,
        SKILL_WEIGHT,
    )
    score += skill_score

    matched_factors.extend(
        format_factor("Skill", skill)
        for skill in matched_skills
    )

    role_score, matched_roles = calculate_overlap_score(
        context.role_types,
        [normalize_text(job.role_type)],
        ROLE_WEIGHT,
    )
    score += role_score

    matched_factors.extend(
        format_factor("Role type", role)
        for role in matched_roles
    )

    domain_score, matched_domains = calculate_overlap_score(
        context.domains,
        [normalize_text(job.domain)],
        DOMAIN_WEIGHT,
    )
    score += domain_score

    matched_factors.extend(
        format_factor("Domain", domain)
        for domain in matched_domains
    )

    location_score, matched_locations = calculate_overlap_score(
        context.locations,
        [normalize_text(job.location)],
        LOCATION_WEIGHT,
    )
    score += location_score

    matched_factors.extend(
        format_factor("Location", location)
        for location in matched_locations
    )

    (
        experience_score,
        matched_experience_levels,
    ) = calculate_overlap_score(
        context.experience_levels,
        [normalize_text(job.experience_level)],
        EXPERIENCE_WEIGHT,
    )
    score += experience_score

    matched_factors.extend(
        format_factor(
            "Experience",
            experience_level,
        )
        for experience_level in matched_experience_levels
    )

    rounded_score = round(score)

    return RankedJob(
        job=job,
        match_score=rounded_score,
        explanation=build_explanation(matched_factors),
        matched_factors=matched_factors,
    )


def rank_jobs(
    jobs: list[Job],
    context: RankingContext,
) -> list[RankedJob]:
    ranked_jobs = [
        rank_job(job, context)
        for job in jobs
    ]

    return sorted(
        ranked_jobs,
        key=lambda ranked_job: (
            -ranked_job.match_score,
            ranked_job.job.id,
        ),
    )