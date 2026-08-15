"""
FollowUpService — Manages follow-up recommendations and message drafting requiring user approval.

INVARIANT: Follow-ups MUST be approved by candidate before sending.
No unsolicited messaging or automatic spam.
"""
import logging
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.application import Application
from app.models.application_tracking import FollowUp

logger = logging.getLogger("app.services.followup")


class FollowUpService:
    """
    Identifies application follow-up eligibility and generates drafts requiring user approval.
    """

    @staticmethod
    async def generate_followup_draft(
        session: AsyncSession,
        user: User,
        application_id: str,
        days_delay: int = 7
    ) -> Dict[str, Any]:
        a_uuid = uuid.UUID(application_id)
        res = await session.execute(
            select(Application).filter(Application.id == a_uuid, Application.user_id == user.id)
        )
        app_entity = res.scalars().first()
        if not app_entity:
            raise ValueError(f"Application {application_id} not found or access denied.")

        sched_date = datetime.datetime.utcnow() + datetime.timedelta(days=days_delay)

        subj = f"Follow-up regarding {app_entity.role} application at {app_entity.company}"
        body = (
            f"Dear Hiring Team at {app_entity.company},\n\n"
            f"I recently submitted my application for the {app_entity.role} position. "
            f"I wanted to reiterate my enthusiasm for the opportunity and express my keen interest "
            f"in contributing to your engineering initiatives.\n\n"
            f"Please let me know if you require any additional materials.\n\n"
            f"Best regards,\nCandidate"
        )

        fu_rec = FollowUp(
            id=uuid.uuid4(),
            application_id=a_uuid,
            user_id=user.id,
            followup_number=1,
            channel="EMAIL",
            scheduled_date=sched_date,
            draft_subject=subj,
            draft_body=body,
            status="READY_FOR_REVIEW",
        )
        session.add(fu_rec)
        await session.commit()

        return {
            "id": str(fu_rec.id),
            "application_id": application_id,
            "company": app_entity.company,
            "role": app_entity.role,
            "draft_subject": subj,
            "draft_body": body,
            "status": "READY_FOR_REVIEW",
            "requires_user_approval": True,
        }

    @staticmethod
    async def approve_followup(
        session: AsyncSession,
        user: User,
        followup_id: str
    ) -> Dict[str, Any]:
        f_uuid = uuid.UUID(followup_id)
        res = await session.execute(
            select(FollowUp).filter(FollowUp.id == f_uuid, FollowUp.user_id == user.id)
        )
        fu = res.scalars().first()
        if not fu:
            raise ValueError(f"Follow-up {followup_id} not found or access denied.")

        fu.status = "USER_APPROVED"
        fu.approval_token = f"FU-APP-{uuid.uuid4().hex[:8].upper()}"
        await session.commit()

        return {
            "id": followup_id,
            "status": "USER_APPROVED",
            "approval_token": fu.approval_token,
        }
