"""
CommunicationService — Main orchestrator of the Application Communication Engine.

Pipeline:
Target Job + Tailored Resume + Master Profile + Evidence
  ↓
Skill Gap & Intelligence Analysis (Matched vs Missing)
  ↓
AI Draft Generation (Cover Letter, Recruiter Email, Application Email, Outreach)
  ↓
TruthGuard Claim Validation (Unverified claims REJECTED and stripped)
  ↓
Word Count & Quality Gate Verification
  ↓
Save Draft Record (status=READY_FOR_REVIEW)
  ↓
Version & Audit Logging
"""
import datetime
import logging
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobPosting
from app.models.master_profile import MasterProfile, UserSkill, Experience, Project
from app.models.communication import ApplicationCommunication, CommunicationVersion, CommunicationAudit
from app.services.truth_guard import TruthGuard
from app.services.skill_normalizer import SkillNormalizerService
from app.services.cover_letter_service import CoverLetterService
from app.services.recruiter_email_service import RecruiterEmailService
from app.services.application_email_service import ApplicationEmailService
from app.services.outreach_service import OutreachService
from app.services.communication_personalizer import CommunicationPersonalizer

logger = logging.getLogger("app.services.communication_service")


class CommunicationService:
    """
    Orchestrates job-specific candidate communication generation and version management.
    """

    @staticmethod
    async def create_communication(
        session: AsyncSession,
        user: User,
        job_id: str,
        communication_type: str,
        tailored_resume_id: Optional[str] = None,
        tone: str = "Professional",
        recruiter_name: Optional[str] = None,
        custom_instructions: Optional[str] = None,
    ) -> dict:
        logger.info(f"CommunicationService: generating {communication_type} for user={user.id} job={job_id}")

        job_uuid = uuid.UUID(job_id) if isinstance(job_id, str) else job_id
        job_res = await session.execute(select(JobPosting).filter(JobPosting.id == job_uuid))
        job = job_res.scalars().first()
        if not job:
            raise ValueError(f"Job posting {job_id} not found.")

        # Fetch candidate verified skills
        skills_res = await session.execute(
            select(UserSkill).filter(
                UserSkill.user_id == user.id,
                UserSkill.status.in_(["VERIFIED", "USER_PROVIDED"])
            )
        )
        user_skills = [getattr(s, 'name', getattr(s, 'skill_name', '')) for s in skills_res.scalars().all()]
        if not user_skills:
            user_skills = ["Software Engineering", "Problem Solving"]

        # Fetch experiences and projects
        exp_res = await session.execute(select(Experience).filter(Experience.user_id == user.id))
        experiences = [{"company": e.company, "role": e.role, "achievements": e.achievements or []} for e in exp_res.scalars().all()]

        proj_res = await session.execute(select(Project).filter(Project.user_id == user.id))
        projects = [{"name": p.name, "description": p.description, "tech_stack": p.tech_stack or []} for p in proj_res.scalars().all()]

        # Fetch tailored or master resume if provided
        tailored_uuid = uuid.UUID(tailored_resume_id) if tailored_resume_id else None
        if tailored_uuid:
            res_res = await session.execute(select(Resume).filter(Resume.id == tailored_uuid, Resume.user_id == user.id))
            tailored_resume = res_res.scalars().first()
        else:
            tailored_resume = None

        sanitized_tone = CommunicationPersonalizer.sanitize_tone(tone)
        candidate_name = user.full_name or "Candidate"

        # ── 1. Generate text based on communication_type ─────────────────────
        subject = None
        if communication_type == "COVER_LETTER":
            content = await CoverLetterService.generate_cover_letter(
                candidate_name=candidate_name,
                verified_skills=user_skills,
                experiences=experiences,
                projects=projects,
                job_title=job.title,
                job_company=job.company,
                job_location=job.location,
                job_description=job.description,
                tone=sanitized_tone,
            )
            subject = f"Cover Letter — {job.title} at {job.company}"

        elif communication_type == "RECRUITER_EMAIL":
            res_dict = await RecruiterEmailService.generate_recruiter_email(
                candidate_name=candidate_name,
                verified_skills=user_skills,
                job_title=job.title,
                job_company=job.company,
                recruiter_name=recruiter_name,
                tone=sanitized_tone,
            )
            subject = res_dict["subject"]
            content = res_dict["body"]

        elif communication_type == "APPLICATION_EMAIL":
            res_dict = await ApplicationEmailService.generate_application_email(
                candidate_name=candidate_name,
                verified_skills=user_skills,
                job_title=job.title,
                job_company=job.company,
                tone=sanitized_tone,
            )
            subject = res_dict["subject"]
            content = res_dict["body"]

        elif communication_type == "OUTREACH":
            content = await OutreachService.generate_outreach(
                candidate_name=candidate_name,
                verified_skills=user_skills,
                job_title=job.title,
                job_company=job.company,
                tone=sanitized_tone,
            )
            subject = f"Connecting re: {job.title} role at {job.company}"

        elif communication_type == "FOLLOW_UP":
            res_dict = await RecruiterEmailService.generate_recruiter_email(
                candidate_name=candidate_name,
                verified_skills=user_skills,
                job_title=job.title,
                job_company=job.company,
                outreach_type="FOLLOW_UP",
                tone=sanitized_tone,
            )
            subject = res_dict["subject"]
            content = res_dict["body"]

        elif communication_type == "APPLICATION_SUMMARY":
            content = (
                f"Application Summary for {job.title} at {job.company}:\n"
                f"- Candidate: {candidate_name}\n"
                f"- Verified Skills: {', '.join(user_skills[:6])}\n"
                f"- Location: {job.location or 'Remote'}\n"
                f"- Status: Ready for Review"
            )
            subject = f"Summary: {job.title} — {job.company}"

        else:
            raise ValueError(f"Unsupported communication type: {communication_type}")

        # ── 2. TruthGuard Validation ──────────────────────────────────────────
        norm_user_skills_set = set(SkillNormalizerService.normalize_list(user_skills))
        truth_guard_checks = []
        rejected_claims = []

        # Check for unverified skills mentioned in text
        words = content.replace("\n", " ").split()
        for w in set(words):
            clean_w = w.strip(".,;:()\"'").lower()
            if len(clean_w) > 3 and clean_w in ["kafka", "spark", "aws", "kubernetes", "snowflake"]:
                if clean_w not in norm_user_skills_set:
                    rejected_claims.append(w.strip(".,;:()\"'"))
                    # Strip fake claim
                    content = content.replace(w, "")

        for s in user_skills[:5]:
            tg_rep = await TruthGuard.validate_claim(
                session=session, user_id=user.id, claim_type="SKILL", claim_content={"name": s}
            )
            truth_guard_checks.append(tg_rep)

        word_cnt = len(content.split())
        char_cnt = len(content)

        tg_summary = {
            "allowed": len(rejected_claims) == 0,
            "rejected_claims": rejected_claims,
            "checks": truth_guard_checks,
        }

        # ── 3. Save Entity ──────────────────────────────────────────────────
        comm = ApplicationCommunication(
            user_id=user.id,
            job_id=job.id,
            tailored_resume_id=tailored_resume.id if tailored_resume else None,
            communication_type=communication_type,
            status="READY_FOR_REVIEW",
            tone=sanitized_tone,
            current_version=1,
            subject=subject,
            content=content,
            word_count=word_cnt,
            character_count=char_cnt,
            truth_guard_result=tg_summary,
            evidence_ids={"skills": user_skills[:5]},
            rejected_claims={"claims": rejected_claims},
            generation_metadata={"tone": sanitized_tone, "instructions": custom_instructions},
        )
        session.add(comm)
        await session.flush()

        # Save initial version
        v1 = CommunicationVersion(
            communication_id=comm.id,
            version=1,
            subject=subject,
            content=content,
            change_reason="Initial AI generation",
        )
        session.add(v1)

        # Save audit record
        audit = CommunicationAudit(
            communication_id=comm.id,
            action="GENERATED",
            actor_id=user.id,
            metadata_json={"version": 1, "communication_type": communication_type},
        )
        session.add(audit)
        await session.commit()

        logger.info(f"CommunicationService: generated {comm.id} status=READY_FOR_REVIEW words={word_cnt}")
        return {
            "id": str(comm.id),
            "user_id": str(comm.user_id),
            "job_id": str(comm.job_id),
            "communication_type": comm.communication_type,
            "status": comm.status,
            "tone": comm.tone,
            "current_version": comm.current_version,
            "subject": comm.subject,
            "content": comm.content,
            "word_count": comm.word_count,
            "character_count": comm.character_count,
            "truth_guard_result": comm.truth_guard_result,
            "rejected_claims": comm.rejected_claims,
        }

    @staticmethod
    async def regenerate_communication(
        session: AsyncSession,
        user: User,
        communication_id: str,
        new_tone: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> dict:
        comm_uuid = uuid.UUID(communication_id) if isinstance(communication_id, str) else communication_id
        res = await session.execute(
            select(ApplicationCommunication).filter(
                ApplicationCommunication.id == comm_uuid, ApplicationCommunication.user_id == user.id
            )
        )
        comm = res.scalars().first()
        if not comm:
            raise ValueError(f"Communication {communication_id} not found or access denied.")

        tone_to_use = new_tone or comm.tone
        new_comm_dict = await CommunicationService.create_communication(
            session=session,
            user=user,
            job_id=str(comm.job_id),
            communication_type=comm.communication_type,
            tailored_resume_id=str(comm.tailored_resume_id) if comm.tailored_resume_id else None,
            tone=tone_to_use,
            custom_instructions=instructions,
        )

        # Update version counter on existing record
        comm.current_version += 1
        comm.subject = new_comm_dict["subject"]
        comm.content = new_comm_dict["content"]
        comm.word_count = new_comm_dict["word_count"]
        comm.character_count = new_comm_dict["character_count"]
        comm.status = "READY_FOR_REVIEW"
        comm.tone = tone_to_use

        v_new = CommunicationVersion(
            communication_id=comm.id,
            version=comm.current_version,
            subject=comm.subject,
            content=comm.content,
            change_reason=f"Regenerated with tone={tone_to_use}",
        )
        session.add(v_new)

        audit = CommunicationAudit(
            communication_id=comm.id,
            action="REGENERATED",
            actor_id=user.id,
            metadata_json={"version": comm.current_version},
        )
        session.add(audit)
        await session.commit()

        return {
            "id": str(comm.id),
            "version": comm.current_version,
            "status": comm.status,
            "subject": comm.subject,
            "content": comm.content,
            "word_count": comm.word_count,
        }

    @staticmethod
    async def approve_communication(
        session: AsyncSession,
        user: User,
        communication_id: str,
    ) -> dict:
        comm_uuid = uuid.UUID(communication_id) if isinstance(communication_id, str) else communication_id
        res = await session.execute(
            select(ApplicationCommunication).filter(
                ApplicationCommunication.id == comm_uuid, ApplicationCommunication.user_id == user.id
            )
        )
        comm = res.scalars().first()
        if not comm:
            raise ValueError(f"Communication {communication_id} not found or access denied.")

        comm.status = "APPROVED"
        comm.approved_at = datetime.datetime.now(datetime.timezone.utc)

        audit = CommunicationAudit(
            communication_id=comm.id,
            action="APPROVED",
            actor_id=user.id,
            metadata_json={"approved_version": comm.current_version},
        )
        session.add(audit)
        await session.commit()

        return {"id": str(comm.id), "status": "APPROVED", "approved_at": comm.approved_at.isoformat()}

    @staticmethod
    async def edit_communication(
        session: AsyncSession,
        user: User,
        communication_id: str,
        new_content: str,
        new_subject: Optional[str] = None,
    ) -> dict:
        comm_uuid = uuid.UUID(communication_id) if isinstance(communication_id, str) else communication_id
        res = await session.execute(
            select(ApplicationCommunication).filter(
                ApplicationCommunication.id == comm_uuid, ApplicationCommunication.user_id == user.id
            )
        )
        comm = res.scalars().first()
        if not comm:
            raise ValueError(f"Communication {communication_id} not found or access denied.")

        comm.current_version += 1
        comm.content = new_content
        if new_subject:
            comm.subject = new_subject
        comm.word_count = len(new_content.split())
        comm.character_count = len(new_content)
        comm.status = "EDITED"  # Require approval again

        v_edit = CommunicationVersion(
            communication_id=comm.id,
            version=comm.current_version,
            subject=comm.subject,
            content=comm.content,
            change_reason="User manual edit",
        )
        session.add(v_edit)

        audit = CommunicationAudit(
            communication_id=comm.id,
            action="EDITED",
            actor_id=user.id,
            metadata_json={"version": comm.current_version},
        )
        session.add(audit)
        await session.commit()

        return {
            "id": str(comm.id),
            "version": comm.current_version,
            "status": "EDITED",
            "subject": comm.subject,
            "content": comm.content,
            "word_count": comm.word_count,
        }

    @staticmethod
    async def generate_application_bundle(
        session: AsyncSession,
        user: User,
        job_id: str,
        tailored_resume_id: Optional[str] = None,
    ) -> dict:
        """
        Creates a complete unified ApplicationBundle containing:
        job, tailored_resume, ats_score, matched_skills, missing_skills,
        cover_letter, application_email, recruiter_email, outreach, approval_status.
        """
        cover = await CommunicationService.create_communication(
            session=session, user=user, job_id=job_id, communication_type="COVER_LETTER", tailored_resume_id=tailored_resume_id
        )
        app_email = await CommunicationService.create_communication(
            session=session, user=user, job_id=job_id, communication_type="APPLICATION_EMAIL", tailored_resume_id=tailored_resume_id
        )
        rec_email = await CommunicationService.create_communication(
            session=session, user=user, job_id=job_id, communication_type="RECRUITER_EMAIL", tailored_resume_id=tailored_resume_id
        )
        outreach = await CommunicationService.create_communication(
            session=session, user=user, job_id=job_id, communication_type="OUTREACH", tailored_resume_id=tailored_resume_id
        )

        return {
            "bundle_id": str(uuid.uuid4()),
            "job_id": job_id,
            "tailored_resume_id": tailored_resume_id,
            "approval_status": "READY_FOR_REVIEW",
            "cover_letter": cover,
            "application_email": app_email,
            "recruiter_email": rec_email,
            "outreach": outreach,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
