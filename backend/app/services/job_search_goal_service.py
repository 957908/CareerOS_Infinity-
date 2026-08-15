"""
JobSearchGoalService — Manages candidate target goals and daily submission limits.

INVARIANT: daily_submission_target is a submission CEILING, NOT permission to auto-submit.
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job_search_goal import JobSearchGoal

logger = logging.getLogger("app.services.job_search_goal")


class JobSearchGoalService:
    """
    Manages candidate job search preferences and targets.
    """

    @staticmethod
    async def get_or_create_goal(session: AsyncSession, user: User) -> JobSearchGoal:
        res = await session.execute(
            select(JobSearchGoal).filter(JobSearchGoal.user_id == user.id)
        )
        goal = res.scalars().first()
        if not goal:
            goal = JobSearchGoal(
                user_id=user.id,
                target_role="Backend Engineer",
                target_salary_min=120000.0,
                target_salary_target=140000.0,
                preferred_work_mode="REMOTE",
                minimum_match_score=60.0,
                daily_preparation_target=10,
                daily_submission_target=5,
            )
            session.add(goal)
            await session.commit()
        return goal

    @staticmethod
    async def update_goal(
        session: AsyncSession,
        user: User,
        target_role: Optional[str] = None,
        target_salary_min: Optional[float] = None,
        target_salary_target: Optional[float] = None,
        preferred_work_mode: Optional[str] = None,
        daily_preparation_target: Optional[int] = None,
        daily_submission_target: Optional[int] = None,
    ) -> Dict[str, Any]:
        goal = await JobSearchGoalService.get_or_create_goal(session, user)

        if target_role:
            goal.target_role = target_role
        if target_salary_min is not None:
            goal.target_salary_min = target_salary_min
        if target_salary_target is not None:
            goal.target_salary_target = target_salary_target
        if preferred_work_mode:
            goal.preferred_work_mode = preferred_work_mode
        if daily_preparation_target is not None:
            goal.daily_preparation_target = daily_preparation_target
        if daily_submission_target is not None:
            goal.daily_submission_target = daily_submission_target

        await session.commit()

        return {
            "target_role": goal.target_role,
            "target_salary_min": goal.target_salary_min,
            "target_salary_target": goal.target_salary_target,
            "preferred_work_mode": goal.preferred_work_mode,
            "daily_preparation_target": goal.daily_preparation_target,
            "daily_submission_target": goal.daily_submission_target,
        }
