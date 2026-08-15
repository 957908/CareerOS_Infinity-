"""
Career Analytics & Job Search Goals REST API Router — Part 7

Endpoints:
- GET /api/v1/analytics/career
- GET /api/v1/analytics/sources
- GET /api/v1/jobpilot/goals
- PUT /api/v1/jobpilot/goals
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.career_analytics_service import CareerAnalyticsService
from app.services.job_search_goal_service import JobSearchGoalService

logger = logging.getLogger("app.api.career_analytics")
router = APIRouter(tags=["Career Analytics & Goals"])


@router.get("/analytics/career", status_code=status.HTTP_200_OK)
async def get_career_analytics_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    return await CareerAnalyticsService.get_career_analytics(session, current_user)


@router.get("/analytics/sources", status_code=status.HTTP_200_OK)
async def get_source_performance_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    return await CareerAnalyticsService.get_source_performance(session, current_user)


@router.get("/jobpilot/goals", status_code=status.HTTP_200_OK)
async def get_goals_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    goal = await JobSearchGoalService.get_or_create_goal(session, current_user)
    return {
        "target_role": goal.target_role,
        "target_salary_min": goal.target_salary_min,
        "target_salary_target": goal.target_salary_target,
        "preferred_work_mode": goal.preferred_work_mode,
        "daily_preparation_target": goal.daily_preparation_target,
        "daily_submission_target": goal.daily_submission_target,
    }


@router.put("/jobpilot/goals", status_code=status.HTTP_200_OK)
async def update_goals_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    return await JobSearchGoalService.update_goal(
        session=session,
        user=current_user,
        target_role=payload.get("target_role"),
        target_salary_min=payload.get("target_salary_min"),
        target_salary_target=payload.get("target_salary_target"),
        preferred_work_mode=payload.get("preferred_work_mode"),
        daily_preparation_target=payload.get("daily_preparation_target"),
        daily_submission_target=payload.get("daily_submission_target"),
    )
