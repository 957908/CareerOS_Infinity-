"""
Communications REST API Router — Part 4

Endpoints:
- POST /api/v1/communications/cover-letter
- POST /api/v1/communications/recruiter-email
- POST /api/v1/communications/application-email
- POST /api/v1/communications/outreach
- POST /api/v1/communications/bundle
- GET /api/v1/communications
- GET /api/v1/communications/{id}
- GET /api/v1/communications/{id}/versions
- POST /api/v1/communications/{id}/regenerate
- POST /api/v1/communications/{id}/approve
- POST /api/v1/communications/{id}/reject
- PATCH /api/v1/communications/{id}
- DELETE /api/v1/communications/{id}

BOLA & User Ownership strictly enforced (`current_user.id == resource.user_id`).
NO AUTOMATIC SENDING / SUBMISSION ROUTINES EXECUTE.
"""
import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.communication import ApplicationCommunication, CommunicationVersion
from app.services.communication_service import CommunicationService
from app.services.automation_adapter import ApplicationAutomationAdapter

logger = logging.getLogger("app.api.communications")
router = APIRouter(prefix="/communications", tags=["Application Communications"])


@router.post("/cover-letter", status_code=status.HTTP_201_CREATED)
async def generate_cover_letter_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required.")

    try:
        return await CommunicationService.create_communication(
            session=session,
            user=current_user,
            job_id=job_id,
            communication_type="COVER_LETTER",
            tailored_resume_id=payload.get("tailored_resume_id"),
            tone=payload.get("tone", "Professional"),
            custom_instructions=payload.get("instructions"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/recruiter-email", status_code=status.HTTP_201_CREATED)
async def generate_recruiter_email_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required.")

    try:
        return await CommunicationService.create_communication(
            session=session,
            user=current_user,
            job_id=job_id,
            communication_type="RECRUITER_EMAIL",
            tailored_resume_id=payload.get("tailored_resume_id"),
            tone=payload.get("tone", "Concise"),
            recruiter_name=payload.get("recruiter_name"),
            custom_instructions=payload.get("instructions"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/application-email", status_code=status.HTTP_201_CREATED)
async def generate_application_email_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required.")

    try:
        return await CommunicationService.create_communication(
            session=session,
            user=current_user,
            job_id=job_id,
            communication_type="APPLICATION_EMAIL",
            tailored_resume_id=payload.get("tailored_resume_id"),
            tone=payload.get("tone", "Formal"),
            custom_instructions=payload.get("instructions"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/outreach", status_code=status.HTTP_201_CREATED)
async def generate_outreach_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required.")

    try:
        return await CommunicationService.create_communication(
            session=session,
            user=current_user,
            job_id=job_id,
            communication_type="OUTREACH",
            tailored_resume_id=payload.get("tailored_resume_id"),
            tone=payload.get("tone", "Professional"),
            custom_instructions=payload.get("instructions"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/bundle", status_code=status.HTTP_201_CREATED)
async def generate_application_bundle_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required.")

    try:
        bundle = await CommunicationService.generate_application_bundle(
            session=session,
            user=current_user,
            job_id=job_id,
            tailored_resume_id=payload.get("tailored_resume_id"),
        )
        return ApplicationAutomationAdapter.prepare_application(bundle)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("", status_code=status.HTTP_200_OK)
async def list_communications(
    job_id: Optional[str] = None,
    communication_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    query = select(ApplicationCommunication).filter(ApplicationCommunication.user_id == current_user.id)
    if job_id:
        try:
            query = query.filter(ApplicationCommunication.job_id == uuid.UUID(job_id))
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid job_id format.")

    if communication_type:
        query = query.filter(ApplicationCommunication.communication_type == communication_type)

    query = query.order_by(ApplicationCommunication.created_at.desc())
    res = await session.execute(query)
    comms = res.scalars().all()

    return [
        {
            "id": str(c.id),
            "job_id": str(c.job_id),
            "communication_type": c.communication_type,
            "status": c.status,
            "tone": c.tone,
            "current_version": c.current_version,
            "subject": c.subject,
            "word_count": c.word_count,
            "character_count": c.character_count,
            "created_at": c.created_at.isoformat(),
            "approved_at": c.approved_at.isoformat() if c.approved_at else None,
        }
        for c in comms
    ]


@router.get("/{comm_id}", status_code=status.HTTP_200_OK)
async def get_communication_detail(
    comm_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        c_uuid = uuid.UUID(comm_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid communication ID format.")

    res = await session.execute(
        select(ApplicationCommunication).filter(
            ApplicationCommunication.id == c_uuid, ApplicationCommunication.user_id == current_user.id
        )
    )
    comm = res.scalars().first()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication item not found or access denied.")

    return {
        "id": str(comm.id),
        "user_id": str(comm.user_id),
        "job_id": str(comm.job_id),
        "tailored_resume_id": str(comm.tailored_resume_id) if comm.tailored_resume_id else None,
        "communication_type": comm.communication_type,
        "status": comm.status,
        "tone": comm.tone,
        "current_version": comm.current_version,
        "subject": comm.subject,
        "content": comm.content,
        "word_count": comm.word_count,
        "character_count": comm.character_count,
        "truth_guard_result": comm.truth_guard_result or {},
        "rejected_claims": comm.rejected_claims or {},
        "created_at": comm.created_at.isoformat(),
        "approved_at": comm.approved_at.isoformat() if comm.approved_at else None,
    }


@router.get("/{comm_id}/versions", status_code=status.HTTP_200_OK)
async def get_communication_versions(
    comm_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    try:
        c_uuid = uuid.UUID(comm_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid communication ID format.")

    res = await session.execute(
        select(ApplicationCommunication).filter(
            ApplicationCommunication.id == c_uuid, ApplicationCommunication.user_id == current_user.id
        )
    )
    comm = res.scalars().first()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication item not found or access denied.")

    v_res = await session.execute(
        select(CommunicationVersion).filter(CommunicationVersion.communication_id == comm.id).order_by(CommunicationVersion.version.desc())
    )
    versions = v_res.scalars().all()

    return [
        {
            "id": str(v.id),
            "version": v.version,
            "subject": v.subject,
            "content": v.content,
            "change_reason": v.change_reason,
            "created_at": v.created_at.isoformat(),
        }
        for v in versions
    ]


@router.post("/{comm_id}/regenerate", status_code=status.HTTP_200_OK)
async def regenerate_communication_endpoint(
    comm_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        return await CommunicationService.regenerate_communication(
            session=session,
            user=current_user,
            communication_id=comm_id,
            new_tone=payload.get("tone"),
            instructions=payload.get("instructions"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{comm_id}/approve", status_code=status.HTTP_200_OK)
async def approve_communication_endpoint(
    comm_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        return await CommunicationService.approve_communication(
            session=session, user=current_user, communication_id=comm_id
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{comm_id}/reject", status_code=status.HTTP_200_OK)
async def reject_communication_endpoint(
    comm_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        c_uuid = uuid.UUID(comm_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid communication ID format.")

    res = await session.execute(
        select(ApplicationCommunication).filter(
            ApplicationCommunication.id == c_uuid, ApplicationCommunication.user_id == current_user.id
        )
    )
    comm = res.scalars().first()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication item not found or access denied.")

    comm.status = "REJECTED"
    await session.commit()

    return {"status": "ok", "approval_status": "REJECTED", "communication_id": comm_id}


@router.patch("/{comm_id}", status_code=status.HTTP_200_OK)
async def edit_communication_endpoint(
    comm_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    new_content = payload.get("content")
    if not new_content:
        raise HTTPException(status_code=400, detail="content field is required for edit.")

    try:
        return await CommunicationService.edit_communication(
            session=session,
            user=current_user,
            communication_id=comm_id,
            new_content=new_content,
            new_subject=payload.get("subject"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.delete("/{comm_id}", status_code=status.HTTP_200_OK)
async def delete_communication_endpoint(
    comm_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        c_uuid = uuid.UUID(comm_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid communication ID format.")

    res = await session.execute(
        select(ApplicationCommunication).filter(
            ApplicationCommunication.id == c_uuid, ApplicationCommunication.user_id == current_user.id
        )
    )
    comm = res.scalars().first()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication item not found or access denied.")

    await session.delete(comm)
    await session.commit()

    return {"status": "ok", "message": "Communication deleted successfully", "communication_id": comm_id}
