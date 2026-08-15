"""
CareerAnalyticsService — Computes full conversion funnel statistics, source effectiveness, and resume variant analytics.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.application import Application
from app.models.resume import Resume

logger = logging.getLogger("app.services.career_analytics")


class CareerAnalyticsService:
    """
    Computes career analytics, source conversion rates, and resume performance.
    """

    @staticmethod
    async def get_career_analytics(session: AsyncSession, user: User) -> Dict[str, Any]:
        res = await session.execute(select(Application).filter(Application.user_id == user.id))
        apps = res.scalars().all()

        total = len(apps)
        qualified = len([a for a in apps if a.status != "BLOCKED"])
        prepared = len([a for a in apps if a.status in ["PACKAGE_GENERATED", "READY_FOR_REVIEW", "USER_APPROVED", "READY_TO_SUBMIT", "SUBMITTED", "SUBMISSION_VERIFIED", "TRACKING"]])
        approved = len([a for a in apps if a.status in ["USER_APPROVED", "READY_TO_SUBMIT", "SUBMITTED", "SUBMISSION_VERIFIED", "TRACKING"]])
        submitted = len([a for a in apps if a.status in ["SUBMITTED", "SUBMISSION_VERIFIED", "TRACKING"]])
        interviews = len([a for a in apps if a.application_stage == "INTERVIEW"])
        offers = len([a for a in apps if a.application_stage == "OFFER"])

        if total == 0:
            return {
                "qualification_rate": "N/A",
                "approval_rate": "N/A",
                "submission_rate": "N/A",
                "response_rate": "N/A",
                "interview_rate": "N/A",
                "offer_rate": "N/A",
                "data_points": 0
            }

        return {
            "qualification_rate_percent": round((qualified / max(total, 1)) * 100.0, 1),
            "approval_rate_percent": round((approved / max(prepared, 1)) * 100.0, 1),
            "submission_rate_percent": round((submitted / max(approved, 1)) * 100.0, 1),
            "interview_rate_percent": round((interviews / max(submitted, 1)) * 100.0, 1),
            "offer_rate_percent": round((offers / max(interviews, 1)) * 100.0, 1),
            "total_applications": total,
            "total_submitted": submitted,
            "total_interviews": interviews,
            "total_offers": offers,
        }

    @staticmethod
    async def get_source_performance(session: AsyncSession, user: User) -> List[Dict[str, Any]]:
        res = await session.execute(select(Application).filter(Application.user_id == user.id))
        apps = res.scalars().all()

        source_counts: Dict[str, Dict[str, int]] = {}
        for a in apps:
            src = a.source or "MANUAL"
            if src not in source_counts:
                source_counts[src] = {"total": 0, "submitted": 0, "interviews": 0, "offers": 0}
            source_counts[src]["total"] += 1
            if a.status in ["SUBMITTED", "SUBMISSION_VERIFIED", "TRACKING"]:
                source_counts[src]["submitted"] += 1
            if a.application_stage == "INTERVIEW":
                source_counts[src]["interviews"] += 1
            if a.application_stage == "OFFER":
                source_counts[src]["offers"] += 1

        result = []
        for src, counts in source_counts.items():
            conv = (counts["interviews"] / max(counts["submitted"], 1)) * 100.0
            result.append({
                "source": src,
                "total_jobs": counts["total"],
                "submitted": counts["submitted"],
                "interviews": counts["interviews"],
                "offers": counts["offers"],
                "conversion_rate_percent": round(conv, 1),
                "performance_rating": "BEST_SOURCE" if conv >= 30.0 and counts["submitted"] >= 3 else "STANDARD",
            })
        return result
