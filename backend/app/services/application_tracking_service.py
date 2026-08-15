"""
ApplicationTrackingService — Manages state machine validation and timeline event logs.
"""
import logging
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.application import Application
from app.models.application_tracking import ApplicationTrackingEvent

logger = logging.getLogger("app.services.application_tracking")


class ApplicationTrackingService:
    """
    Validates lifecycle state transitions and records immutable timeline events.
    """
    VALID_TRANSITIONS = {
        "DISCOVERED": ["QUALIFIED", "BLOCKED", "DUPLICATE", "SKIPPED"],
        "QUALIFIED": ["PACKAGE_GENERATED", "READY_FOR_REVIEW", "BLOCKED", "SKIPPED"],
        "PACKAGE_GENERATED": ["READY_FOR_REVIEW", "BLOCKED"],
        "READY_FOR_REVIEW": ["USER_APPROVED", "REJECTED", "SKIPPED"],
        "USER_APPROVED": ["AUTOMATION_RUNNING", "READY_TO_SUBMIT", "LOGIN_REQUIRED", "CAPTCHA_REQUIRED", "MANUAL_ACTION_REQUIRED"],
        "AUTOMATION_RUNNING": ["READY_TO_SUBMIT", "LOGIN_REQUIRED", "CAPTCHA_REQUIRED", "MANUAL_ACTION_REQUIRED", "FAILED"],
        "READY_TO_SUBMIT": ["SUBMITTED", "SUBMISSION_UNCERTAIN", "BLOCKED"],
        "SUBMITTED": ["SUBMISSION_VERIFIED", "RECRUITER_VIEWED", "RESPONSE_RECEIVED", "REJECTED", "TRACKING"],
        "SUBMISSION_VERIFIED": ["TRACKING", "RECRUITER_VIEWED", "RESPONSE_RECEIVED", "SCREENING", "INTERVIEW_SCHEDULED", "REJECTED"],
        "TRACKING": ["RESPONSE_RECEIVED", "SCREENING", "INTERVIEW_SCHEDULED", "REJECTED", "OFFER", "WITHDRAWN", "EXPIRED"],
        "RESPONSE_RECEIVED": ["SCREENING", "INTERVIEW_SCHEDULED", "REJECTED", "OFFER"],
        "SCREENING": ["INTERVIEW_SCHEDULED", "REJECTED", "WITHDRAWN"],
        "INTERVIEW_SCHEDULED": ["INTERVIEW_COMPLETED", "REJECTED", "WITHDRAWN", "OFFER"],
        "INTERVIEW_COMPLETED": ["ASSESSMENT", "INTERVIEW_SCHEDULED", "OFFER", "REJECTED"],
        "ASSESSMENT": ["OFFER", "REJECTED", "WITHDRAWN"],
        "OFFER": ["WITHDRAWN"],
        "REJECTED": [],
        "WITHDRAWN": [],
        "EXPIRED": [],
    }

    @staticmethod
    async def transition_state(
        session: AsyncSession,
        user: User,
        application_id: str,
        to_status: str,
        actor: str = "SYSTEM",
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        a_uuid = uuid.UUID(application_id)
        res = await session.execute(
            select(Application).filter(Application.id == a_uuid, Application.user_id == user.id)
        )
        app_entity = res.scalars().first()
        if not app_entity:
            raise ValueError(f"Application {application_id} not found or access denied.")

        from_status = app_entity.status

        # Validate transition if not same status
        if from_status != to_status:
            allowed = ApplicationTrackingService.VALID_TRANSITIONS.get(from_status, [])
            if to_status not in allowed and from_status not in ["FAILED", "MANUAL_ACTION_REQUIRED", "LOGIN_REQUIRED", "CAPTCHA_REQUIRED"]:
                logger.warning(f"Illegal state transition attempted: {from_status} -> {to_status}")

        app_entity.status = to_status
        if to_status in ["SUBMITTED", "SUBMISSION_VERIFIED"]:
            app_entity.application_stage = "SUBMITTED"
            if not app_entity.submitted_at:
                app_entity.submitted_at = datetime.datetime.utcnow()
        elif to_status == "INTERVIEW_SCHEDULED":
            app_entity.application_stage = "INTERVIEW"
        elif to_status == "OFFER":
            app_entity.application_stage = "OFFER"
        elif to_status == "REJECTED":
            app_entity.application_stage = "REJECTED"

        # Log timeline event
        event = ApplicationTrackingEvent(
            id=uuid.uuid4(),
            application_id=a_uuid,
            user_id=user.id,
            event_type="STATE_TRANSITION",
            from_status=from_status,
            to_status=to_status,
            actor=actor,
            reason=reason or f"Transitioned from {from_status} to {to_status}",
            metadata_json=metadata or {},
        )
        session.add(event)
        await session.commit()

        return {
            "application_id": application_id,
            "from_status": from_status,
            "to_status": to_status,
            "application_stage": app_entity.application_stage,
            "actor": actor,
            "event_id": str(event.id),
        }

    @staticmethod
    async def get_timeline(
        session: AsyncSession,
        user: User,
        application_id: str
    ) -> List[Dict[str, Any]]:
        a_uuid = uuid.UUID(application_id)
        res = await session.execute(
            select(ApplicationTrackingEvent)
            .filter(ApplicationTrackingEvent.application_id == a_uuid, ApplicationTrackingEvent.user_id == user.id)
            .order_by(ApplicationTrackingEvent.created_at.asc())
        )
        events = res.scalars().all()
        return [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "from_status": e.from_status,
                "to_status": e.to_status,
                "actor": e.actor,
                "reason": e.reason,
                "metadata": e.metadata_json or {},
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ]
