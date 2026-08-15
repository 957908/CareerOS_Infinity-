"""
RecommendationService — Personalized job feed ranking with freshness decay.

Ranks jobs for a user based on:
- overall_fit_score (primary)
- job freshness (posted_at age)
- quality_status (HIGH > MEDIUM > LOW)
- interaction history (excludes DISMISSED, deprioritizes VIEWED)
- career goal alignment

SAFETY: Never shows expired/suspicious jobs in recommendations.
PRIVACY: All queries are strictly scoped to current_user.id.
"""
import datetime
import logging
import math
from typing import Optional
from sqlalchemy import select, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job import JobPosting
from app.models.job_intelligence import JobMatch, JobInteraction

logger = logging.getLogger("app.services.recommendation")

# Freshness decay: job loses priority exponentially over time
# Score multiplier at day 0 = 1.0, day 30 = ~0.7, day 60 = ~0.5, day 90 = ~0.35
FRESHNESS_HALF_LIFE_DAYS = 30.0

# Quality boosts
QUALITY_BOOSTS = {
    "HIGH": 5.0,
    "MEDIUM": 0.0,
    "LOW": -10.0,
    "EXPIRED": -1000.0,    # Never recommend expired
    "SUSPICIOUS": -1000.0, # Never recommend suspicious
}

# Interaction penalties/boosts
INTERACTION_ADJUSTMENTS = {
    "DISMISSED": -1000.0,  # Never show dismissed jobs
    "APPLIED": -500.0,     # Don't recommend applied jobs
    "SAVED": 5.0,
    "SHORTLISTED": 10.0,
    "VIEWED": -5.0,        # Slight deprioritize already-seen
    "DISCOVERED": 0.0,
}


def _freshness_multiplier(posted_at: Optional[datetime.datetime]) -> float:
    """Exponential decay factor based on job age."""
    if not posted_at:
        return 0.85  # unknown posted date — moderate freshness
    now = datetime.datetime.now(datetime.timezone.utc)
    posted_aware = posted_at if posted_at.tzinfo else posted_at.replace(tzinfo=datetime.timezone.utc)
    age_days = max(0.0, (now - posted_aware).total_seconds() / 86400)
    return math.exp(-age_days * math.log(2) / FRESHNESS_HALF_LIFE_DAYS)


class RecommendationService:
    """
    Builds a personalized ranked job recommendation feed.
    """

    @staticmethod
    async def get_recommended_jobs(
        session: AsyncSession,
        user: User,
        limit: int = 20,
        offset: int = 0,
        min_score: float = 35.0,
    ) -> list[dict]:
        """
        Returns a ranked list of recommended jobs for the user.

        Args:
            session: DB session
            user: Authenticated user
            limit: Page size
            offset: Pagination offset
            min_score: Minimum overall_fit_score to include

        Returns:
            List of ranked job dicts with match + freshness-adjusted scores
        """
        # Load all matches for this user (excluding dismissed/applied)
        dismissed_subq = (
            select(JobInteraction.job_id)
            .filter(
                JobInteraction.user_id == user.id,
                JobInteraction.status.in_(["DISMISSED", "APPLIED"])
            )
            .scalar_subquery()
        )

        matches_result = await session.execute(
            select(JobMatch, JobPosting)
            .join(JobPosting, JobMatch.job_id == JobPosting.id)
            .filter(
                JobMatch.user_id == user.id,
                JobMatch.overall_fit_score >= min_score,
                JobMatch.is_stale == False,
                JobPosting.status == "ACTIVE",
                JobPosting.quality_status.notin_(["EXPIRED", "SUSPICIOUS"]),
                not_(JobPosting.id.in_(dismissed_subq)),
            )
        )
        rows = matches_result.all()

        # Load interactions for scoring adjustment
        interactions_result = await session.execute(
            select(JobInteraction).filter(JobInteraction.user_id == user.id)
        )
        interaction_map = {
            str(i.job_id): i.status
            for i in interactions_result.scalars().all()
        }

        # Score each job with freshness + quality + interaction adjustments
        ranked = []
        for match, job in rows:
            base_score = match.overall_fit_score or 0.0
            freshness = _freshness_multiplier(job.posted_at) * 10.0
            quality_adj = QUALITY_BOOSTS.get(job.quality_status, 0.0)
            interaction_adj = INTERACTION_ADJUSTMENTS.get(
                interaction_map.get(str(job.id), "DISCOVERED"), 0.0
            )

            adjusted_score = base_score + freshness + quality_adj + interaction_adj

            if adjusted_score < -100:
                continue  # Skip dismissed/expired

            ranked.append({
                "job_id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "work_mode": job.work_mode,
                "employment_type": job.employment_type,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_currency": job.salary_currency,
                "source_url": job.source_url,
                "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                "quality_status": job.quality_status,
                "quality_score": job.quality_score,
                "status": job.status,
                "interaction_status": interaction_map.get(str(job.id), "DISCOVERED"),
                "overall_fit_score": base_score,
                "adjusted_score": round(adjusted_score, 2),
                "ats_score": match.ats_score,
                "semantic_score": match.semantic_score,
                "skill_match_score": match.skill_match_score,
                "experience_match_score": match.experience_match_score,
                "role_match_score": match.role_match_score,
                "recommendation_level": match.recommendation_level,
                "matched_skills": match.matched_skills or [],
                "missing_required_skills": match.missing_required_skills or [],
                "missing_preferred_skills": match.missing_preferred_skills or [],
                "match_explanation": match.match_explanation,
            })

        # Sort by adjusted_score descending
        ranked.sort(key=lambda x: x["adjusted_score"], reverse=True)

        # Apply pagination
        total = len(ranked)
        paginated = ranked[offset: offset + limit]

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "jobs": paginated,
        }

    @staticmethod
    async def get_jobs_by_interaction(
        session: AsyncSession,
        user: User,
        interaction_status: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """Get jobs filtered by a specific interaction status (SAVED, SHORTLISTED, etc.)."""
        result = await session.execute(
            select(JobInteraction, JobPosting, JobMatch)
            .join(JobPosting, JobInteraction.job_id == JobPosting.id)
            .outerjoin(
                JobMatch,
                and_(
                    JobMatch.job_id == JobPosting.id,
                    JobMatch.user_id == user.id,
                )
            )
            .filter(
                JobInteraction.user_id == user.id,
                JobInteraction.status == interaction_status,
            )
            .order_by(JobInteraction.interacted_at.desc())
        )
        rows = result.all()
        total = len(rows)

        jobs = []
        for interaction, job, match in rows[offset: offset + limit]:
            jobs.append({
                "job_id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "work_mode": job.work_mode,
                "quality_status": job.quality_status,
                "interaction_status": interaction.status,
                "interacted_at": interaction.interacted_at.isoformat(),
                "overall_fit_score": match.overall_fit_score if match else None,
                "recommendation_level": match.recommendation_level if match else None,
                "matched_skills": match.matched_skills if match else [],
                "missing_required_skills": match.missing_required_skills if match else [],
            })

        return {"total": total, "offset": offset, "limit": limit, "jobs": jobs}
