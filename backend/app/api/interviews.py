"""
Interview Intelligence REST API Router — Part 7

Endpoints:
- POST /api/v1/interviews
- GET  /api/v1/interviews
- POST /api/v1/interviews/{id}/prepare
- GET  /api/v1/interviews/{id}/questions
- POST /api/v1/interviews/{id}/feedback
"""
import logging
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.interview import Interview, InterviewQuestion
from app.services.interview_service import InterviewService

logger = logging.getLogger("app.api.interviews")
router = APIRouter(prefix="/interviews", tags=["Interview Intelligence Engine"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def schedule_interview_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    app_id = payload.get("application_id")
    stage = payload.get("stage", "TECHNICAL")
    sched_str = payload.get("scheduled_at")
    if not app_id or not sched_str:
        raise HTTPException(status_code=400, detail="application_id and scheduled_at are required.")

    try:
        sched_dt = datetime.datetime.fromisoformat(sched_str)
        return await InterviewService.schedule_interview(
            session=session,
            user=current_user,
            application_id=app_id,
            stage=stage,
            scheduled_at=sched_dt,
            location_or_link=payload.get("location_or_link"),
            interviewer_names=payload.get("interviewer_names"),
            notes=payload.get("notes"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("", status_code=status.HTTP_200_OK)
async def list_interviews_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    res = await session.execute(
        select(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.scheduled_at.asc())
    )
    interviews = res.scalars().all()
    return [
        {
            "id": str(i.id),
            "application_id": str(i.application_id),
            "company": i.company,
            "role": i.role,
            "stage": i.stage,
            "status": i.status,
            "scheduled_at": i.scheduled_at.isoformat(),
        }
        for i in interviews
    ]


@router.post("/{id}/prepare", status_code=status.HTTP_200_OK)
async def prepare_interview_endpoint(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    try:
        return await InterviewService.generate_preparation_questions(session, current_user, id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.get("/{id}/questions", status_code=status.HTTP_200_OK)
async def get_interview_questions_endpoint(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    res = await session.execute(
        select(InterviewQuestion).filter(InterviewQuestion.interview_id == id)
    )
    questions = res.scalars().all()
    return [
        {
            "id": str(q.id),
            "category": q.category,
            "question_text": q.question_text,
            "prepared_answer_star": q.prepared_answer_star,
            "is_truth_verified": q.is_truth_verified,
            "has_missing_skill_warning": q.has_missing_skill_warning,
        }
        for q in questions
    ]


@router.post("/{id}/feedback", status_code=status.HTTP_200_OK)
async def record_feedback_endpoint(
    id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    rating = payload.get("rating", 4)
    notes = payload.get("feedback_notes", "Good conversation.")
    try:
        return await InterviewService.record_feedback(
            session=session,
            user=current_user,
            interview_id=id,
            rating=rating,
            feedback_notes=notes,
            difficulty=payload.get("difficulty", "MEDIUM"),
            perceived_outcome=payload.get("perceived_outcome", "PENDING"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
