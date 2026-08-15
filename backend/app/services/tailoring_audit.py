"""
TailoringAuditService — Manages claim-level audit trail for tailored changes.
"""
import logging
import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tailoring import ResumeChange

logger = logging.getLogger("app.services.tailoring_audit")


class TailoringAuditService:
    """
    Persists and queries section/claim-level changes in `resume_changes`.
    """

    @staticmethod
    async def record_changes(
        session: AsyncSession,
        job_id: uuid.UUID,
        resume_id: uuid.UUID,
        changes: List[Dict[str, Any]],
    ) -> List[ResumeChange]:
        records = []
        for c in changes:
            rec = ResumeChange(
                job_id=job_id,
                resume_id=resume_id,
                section_name=c.get("section_name", "General"),
                change_type=c.get("change_type", "MODIFIED"),
                original_text=c.get("original_text"),
                tailored_text=c.get("tailored_text"),
                truth_guard_status=c.get("truth_guard_status", "VERIFIED"),
                evidence_ids=c.get("evidence_ids", []),
                reasoning=c.get("reasoning"),
            )
            session.add(rec)
            records.append(rec)
        await session.flush()
        logger.info(f"TailoringAuditService: recorded {len(records)} changes for resume={resume_id}")
        return records
