"""
ApplicationAnalyticsService — Aggregates application performance metrics and market missing skill gaps.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.application import Application

logger = logging.getLogger("app.services.application_analytics")


class ApplicationAnalyticsService:
    """
    Computes dashboard metrics and market skill gap frequencies.
    """

    @staticmethod
    async def get_analytics(session: AsyncSession, user: User) -> Dict[str, Any]:
        res = await session.execute(
            select(Application).filter(Application.user_id == user.id)
        )
        apps = res.scalars().all()

        total = len(apps)
        submitted = len([a for a in apps if a.status in ["SUBMITTED", "SUBMISSION_VERIFIED", "TRACKING"]])
        interviews = len([a for a in apps if a.application_stage == "INTERVIEW"])
        offers = len([a for a in apps if a.application_stage == "OFFER"])
        rejected = len([a for a in apps if a.status == "REJECTED" or a.application_stage == "REJECTED"])

        avg_fit = sum(a.job_fit_score for a in apps) / max(total, 1)
        avg_ats = sum(a.ats_score for a in apps) / max(total, 1)

        response_rate = (interviews / max(submitted, 1)) * 100.0

        return {
            "total_applications": total,
            "submitted_applications": submitted,
            "interviews_count": interviews,
            "offers_count": offers,
            "rejected_count": rejected,
            "average_fit_score": round(avg_fit, 1),
            "average_ats_score": round(avg_ats, 1),
            "response_rate_percent": round(response_rate, 1),
        }

    @staticmethod
    async def get_market_skill_gaps(session: AsyncSession, user: User) -> List[Dict[str, Any]]:
        res = await session.execute(
            select(Application).filter(Application.user_id == user.id)
        )
        apps = res.scalars().all()

        gap_counts: Dict[str, int] = {}
        for a in apps:
            if a.missing_skills and isinstance(a.missing_skills, dict):
                req_missing = a.missing_skills.get("missing_required") or []
                for s in req_missing:
                    s_clean = s.strip().title()
                    gap_counts[s_clean] = gap_counts.get(s_clean, 0) + 1

        sorted_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"skill": k, "frequency": v} for k, v in sorted_gaps]
