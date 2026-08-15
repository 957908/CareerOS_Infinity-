"""
CareerLearningLoop — Analyzes application funnel metrics and strategic career feedback loops.

INVARIANT: Strategic recommendations MUST NOT automatically alter canonical profile facts.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.application import Application
from app.models.job_discovery import SkillGapAggregate

logger = logging.getLogger("app.services.career_learning")


class CareerLearningLoop:
    """
    Computes application conversion analytics and generates candidate career recommendations.
    """

    @staticmethod
    async def analyze_conversion_funnel(session: AsyncSession, user: User) -> Dict[str, Any]:
        res = await session.execute(select(Application).filter(Application.user_id == user.id))
        apps = res.scalars().all()

        total = len(apps)
        qualified = len([a for a in apps if a.status != "BLOCKED"])
        prepared = len([a for a in apps if a.status in ["PACKAGE_GENERATED", "READY_FOR_REVIEW", "USER_APPROVED", "READY_TO_SUBMIT", "SUBMITTED", "SUBMISSION_VERIFIED", "TRACKING"]])
        approved = len([a for a in apps if a.status in ["USER_APPROVED", "READY_TO_SUBMIT", "SUBMITTED", "SUBMISSION_VERIFIED", "TRACKING"]])
        submitted = len([a for a in apps if a.status in ["SUBMITTED", "SUBMISSION_VERIFIED", "TRACKING"]])
        interviews = len([a for a in apps if a.application_stage == "INTERVIEW"])
        offers = len([a for a in apps if a.application_stage == "OFFER"])

        app_rate = (submitted / max(total, 1)) * 100.0
        resp_rate = (interviews / max(submitted, 1)) * 100.0
        offer_rate = (offers / max(interviews, 1)) * 100.0

        return {
            "total_discovered": total,
            "total_qualified": qualified,
            "total_prepared": prepared,
            "total_approved": approved,
            "total_submitted": submitted,
            "total_interviews": interviews,
            "total_offers": offers,
            "application_rate_percent": round(app_rate, 1),
            "response_rate_percent": round(resp_rate, 1),
            "offer_rate_percent": round(offer_rate, 1),
        }

    @staticmethod
    async def generate_career_recommendations(session: AsyncSession, user: User) -> List[Dict[str, Any]]:
        sg_res = await session.execute(
            select(SkillGapAggregate).filter(SkillGapAggregate.user_id == user.id).order_by(SkillGapAggregate.learning_priority.desc()).limit(5)
        )
        gaps = sg_res.scalars().all()

        recs = []
        for g in gaps:
            recs.append({
                "type": "SKILL_ACQUISITION",
                "skill": g.skill_name,
                "impact": f"Learning {g.skill_name} addresses gaps in {g.job_count} target jobs.",
                "recommendation": f"Add a project or certification for {g.skill_name} to unlock higher fit scores."
            })

        if not recs:
            recs.append({
                "type": "PROFILE_ENHANCEMENT",
                "skill": "FastAPI / AWS",
                "impact": "High market demand in target backend engineering roles.",
                "recommendation": "Highlight cloud architecture experience in master evidence registry."
            })

        return recs
