"""
ApplicationResponseService — Classifies recruiter message responses and logs event timeline.
"""
import logging
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.application import Application
from app.models.application_tracking import ApplicationResponse
from app.services.application_tracking_service import ApplicationTrackingService

logger = logging.getLogger("app.services.application_response")


class ApplicationResponseService:
    """
    Logs and classifies recruiter message responses.
    """

    @staticmethod
    def classify_message(raw_text: str) -> Dict[str, Any]:
        text_lower = raw_text.lower()

        if any(w in text_lower for w in ["interview", "schedule a call", "phone screen", "chat with the team"]):
            return {"classification": "INTERVIEW_INVITATION", "confidence": 0.95, "evidence": "Mentions interview or call scheduling."}
        elif any(w in text_lower for w in ["offer", "congratulations", "pleased to offer"]):
            return {"classification": "OFFER", "confidence": 0.98, "evidence": "Mentions job offer."}
        elif any(w in text_lower for w in ["regret", "not moving forward", "other candidates", "unfortunately"]):
            return {"classification": "REJECTION", "confidence": 0.95, "evidence": "Mentions rejection or non-selection."}
        elif any(w in text_lower for w in ["assessment", "coding test", "take home", "hackerrank"]):
            return {"classification": "ASSESSMENT_REQUEST", "confidence": 0.90, "evidence": "Mentions technical assessment."}
        elif any(w in text_lower for w in ["question", "clarify", "additional details", "references"]):
            return {"classification": "INFORMATION_REQUEST", "confidence": 0.85, "evidence": "Mentions information request."}
        else:
            return {"classification": "NEUTRAL", "confidence": 0.60, "evidence": "General correspondence."}

    @staticmethod
    async def record_response(
        session: AsyncSession,
        user: User,
        application_id: str,
        raw_message_text: str,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> Dict[str, Any]:
        a_uuid = uuid.UUID(application_id)
        res = await session.execute(
            select(Application).filter(Application.id == a_uuid, Application.user_id == user.id)
        )
        app_entity = res.scalars().first()
        if not app_entity:
            raise ValueError(f"Application {application_id} not found or access denied.")

        cls_res = ApplicationResponseService.classify_message(raw_message_text)

        response_rec = ApplicationResponse(
            id=uuid.uuid4(),
            application_id=a_uuid,
            user_id=user.id,
            sender_email=sender_email,
            sender_name=sender_name,
            subject=subject,
            raw_message_text=raw_message_text,
            classification=cls_res["classification"],
            confidence=cls_res["confidence"],
            evidence_snippet=cls_res["evidence"],
            requires_manual_review=(cls_res["confidence"] < 0.70),
        )
        session.add(response_rec)

        # Trigger timeline state update
        to_status = "RESPONSE_RECEIVED"
        if cls_res["classification"] == "INTERVIEW_INVITATION":
            to_status = "INTERVIEW_SCHEDULED"
        elif cls_res["classification"] == "REJECTION":
            to_status = "REJECTED"
        elif cls_res["classification"] == "OFFER":
            to_status = "OFFER"

        await ApplicationTrackingService.transition_state(
            session=session,
            user=user,
            application_id=application_id,
            to_status=to_status,
            actor="RECRUITER",
            reason=f"Recruiter response received ({cls_res['classification']})",
            metadata={"classification": cls_res["classification"], "confidence": cls_res["confidence"]}
        )

        await session.commit()

        return {
            "id": str(response_rec.id),
            "application_id": application_id,
            "classification": cls_res["classification"],
            "confidence": cls_res["confidence"],
            "requires_manual_review": response_rec.requires_manual_review,
        }
