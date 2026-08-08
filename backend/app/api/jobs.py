import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, UUID4
from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.services.ats_service import ATSService
from app.models.user import User

logger = logging.getLogger("app.api.jobs")
router = APIRouter(prefix="/jobs", tags=["ATS Intelligence"])

class MatchRequest(BaseModel):
    resume_id: UUID4
    job_description: str

@router.post("/match", status_code=status.HTTP_200_OK)
async def match_job(
    payload: MatchRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Evaluates semantic match scores and keyword alignment recommendations for a resume version 
    against a target job description. Returns confidence, evidence, and reasoning metadata.
    """
    logger.info(f"API Match: job match request received for user ID: {current_user.id}")
    analysis = await ATSService.analyze_job_match(
        session=session,
        resume_id=str(payload.resume_id),
        job_description=payload.job_description
    )
    return analysis
