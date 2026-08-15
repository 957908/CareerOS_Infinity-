"""
Application Tracking & Response REST API Router — Part 7

Endpoints:
- GET  /api/v1/applications/{id}/timeline
- GET  /api/v1/applications/{id}/responses
- POST /api/v1/applications/{id}/response
- GET  /api/v1/applications/{id}/followups
- POST /api/v1/applications/{id}/followups/draft
- POST /api/v1/applications/{id}/followups/{fid}/approve
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.application_tracking_service import ApplicationTrackingService
from app.services.application_response_service import ApplicationResponseService
from app.services.followup_service import FollowUpService

logger = logging.getLogger("app.api.tracking")
router = APIRouter(prefix="/applications", tags=["Application Tracking & Response"])


@router.get("/{id}/timeline", status_code=status.HTTP_200_OK)
async def get_application_timeline_endpoint(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    try:
        return await ApplicationTrackingService.get_timeline(session, current_user, id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.post("/{id}/response", status_code=status.HTTP_200_OK)
async def record_response_endpoint(
    id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    raw_text = payload.get("raw_message_text")
    if not raw_text:
        raise HTTPException(status_code=400, detail="raw_message_text is required.")

    try:
        return await ApplicationResponseService.record_response(
            session=session,
            user=current_user,
            application_id=id,
            raw_message_text=raw_text,
            sender_email=payload.get("sender_email"),
            sender_name=payload.get("sender_name"),
            subject=payload.get("subject"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.post("/{id}/followups/draft", status_code=status.HTTP_200_OK)
async def draft_followup_endpoint(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        return await FollowUpService.generate_followup_draft(session, current_user, id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.post("/followups/{fid}/approve", status_code=status.HTTP_200_OK)
async def approve_followup_endpoint(
    fid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        return await FollowUpService.approve_followup(session, current_user, fid)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
