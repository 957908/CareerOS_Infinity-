"""
JobOrchestrator — End-to-end application package orchestrator linking Parts 1–5.
"""
import logging
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.job import JobPosting
from app.models.application import Application
from app.services.application_service import ApplicationService
from app.services.resume_tailoring import ResumeTailoringService
from app.services.communication_service import CommunicationService
from app.services.job_scoring_service import JobScoringService
from app.services.skill_gap_service import SkillGapService
from app.services.job_risk_service import JobRiskService

logger = logging.getLogger("app.services.job_orchestrator")


class JobOrchestrator:
    """
    Integrates job discovery, intelligence, tailoring, communication, and submission.
    """

    @staticmethod
    async def process_job_opportunity(
        session: AsyncSession,
        user: User,
        job_id: str,
        auto_generate_package: bool = True
    ) -> Dict[str, Any]:
        j_uuid = uuid.UUID(job_id)
        res = await session.execute(select(JobPosting).filter(JobPosting.id == j_uuid))
        job = res.scalars().first()
        if not job:
            raise ValueError(f"Job posting {job_id} not found.")

        # 1. Risk Filter
        risk_res = JobRiskService.evaluate_risk(job.title, job.company, job.description or "")
        if not risk_res["is_safe_to_apply"]:
            # Create application in BLOCKED status
            app_rec = await ApplicationService.create_application(
                session=session, user=user, job_id=str(job.id), source="DISCOVERY"
            )
            app_uuid = uuid.UUID(app_rec["id"])
            a_ent = (await session.execute(select(Application).filter(Application.id == app_uuid))).scalars().first()
            if a_ent:
                a_ent.status = "BLOCKED"
                a_ent.risk_status = risk_res["risk_status"]
                a_ent.risk_flags = risk_res["risk_flags"]
                await session.commit()
            return {"status": "BLOCKED", "reason": "Job flagged as high risk / scam pattern.", "application_id": app_rec["id"]}

        # 2. Skill Gap & Matching
        gaps = await SkillGapService.evaluate_job_skill_gaps(session=session, user=user, job=job)

        # Record missing skills into aggregate table for learning metrics (WITHOUT touching UserSkill)
        for m_req in gaps["missing_required_skills"]:
            await SkillGapService.record_skill_gap_occurrence(session, user, m_req, is_required=True, role_name=job.title)
        for m_pref in gaps["missing_preferred_skills"]:
            await SkillGapService.record_skill_gap_occurrence(session, user, m_pref, is_required=False, role_name=job.title)

        # 3. Explainable Priority Scoring
        score_res = JobScoringService.calculate_explainable_score(
            skill_match_score=min(100.0, (gaps["matched_count"] / max(gaps["matched_count"] + gaps["missing_required_count"], 1)) * 100.0),
            experience_fit_score=85.0,
            career_fit_score=90.0,
            ats_match_score=85.0,
            matched_skills=gaps["matched_skills"],
            missing_skills=gaps["missing_required_skills"],
        )

        # 4. Create Application Record
        app_data = await ApplicationService.create_application(
            session=session, user=user, job_id=str(job.id), source="DISCOVERY"
        )
        app_uuid = uuid.UUID(app_data["id"])

        # 5. Tailor Resume (if requested)
        tailored_resume_id = None
        if auto_generate_package:
            try:
                t_job = await ResumeTailoringService.tailor_resume(
                    session=session, user=user, target_job_id=str(job.id)
                )
                tailored_resume_id = t_job.tailored_resume_id
            except Exception as e:
                logger.warning(f"Resume tailoring skipped/failed: {e}")

            # Generate Communication Draft
            try:
                comm_data = await CommunicationService.create_communication(
                    session=session, user=user, communication_type="COVER_LETTER", job_id=str(job.id)
                )
            except Exception as e:
                logger.warning(f"Communication draft skipped/failed: {e}")

        # 6. Prepare Package
        prepared = await ApplicationService.prepare_package(
            session=session, user=user, application_id=str(app_uuid)
        )

        return {
            "application_id": str(app_uuid),
            "job_id": str(job.id),
            "company": job.company,
            "role": job.title,
            "priority_score": score_res["final_priority_score"],
            "priority_level": score_res["priority_level"],
            "matched_skills": gaps["matched_skills"],
            "missing_skills": gaps["missing_required_skills"],
            "status": prepared["status"],  # READY_FOR_REVIEW
            "requires_user_approval": True,
        }
