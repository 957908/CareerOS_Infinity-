"""
TailoringPlanner — Deterministic plan generator for resume tailoring.

Analyzes target job requirements against canonical Master Profile entities
(UserSkill, Experience, Project, Certification, Education, CareerGoal).

Outputs a structured TailoringPlan:
- target_role
- priority_skills (matched skills to emphasize)
- missing_required_skills (gap list — NEVER added to profile)
- missing_preferred_skills (gap list — NEVER added to profile)
- sections_to_emphasize
- relevant_projects
- relevant_experiences
"""
import logging
from typing import Optional
from dataclasses import dataclass, field, asdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobPosting
from app.models.job_intelligence import JobSkillRequirement
from app.models.master_profile import (
    MasterProfile, UserSkill, Experience, Project, Certification, CareerGoal
)
from app.services.skill_normalizer import SkillNormalizerService

logger = logging.getLogger("app.services.tailoring_planner")


@dataclass
class TailoringPlan:
    target_role: str
    target_company: str
    priority_skills: list[str] = field(default_factory=list)
    missing_required_skills: list[str] = field(default_factory=list)
    missing_preferred_skills: list[str] = field(default_factory=list)
    sections_to_emphasize: list[str] = field(default_factory=list)
    relevant_projects: list[dict] = field(default_factory=list)
    relevant_experiences: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class TailoringPlanner:
    """
    Builds a deterministic TailoringPlan before any AI text generation occurs.
    """

    @staticmethod
    async def create_plan(
        session: AsyncSession,
        user_id: str,
        job: JobPosting,
    ) -> TailoringPlan:
        logger.info(f"TailoringPlanner: generating plan for user={user_id} job={job.id}")

        # 1. Fetch user skills
        skills_res = await session.execute(
            select(UserSkill).filter(
                UserSkill.user_id == user_id,
                UserSkill.status.in_(["VERIFIED", "USER_PROVIDED"])
            )
        )
        user_skills = [getattr(s, 'name', getattr(s, 'skill_name', '')) for s in skills_res.scalars().all()]
        norm_user_skills = SkillNormalizerService.normalize_list(user_skills)

        # 2. Fetch job skill requirements
        reqs_res = await session.execute(
            select(JobSkillRequirement).filter(JobSkillRequirement.job_id == job.id)
        )
        req_objs = reqs_res.scalars().all()
        job_req = [s.normalized_skill or s.skill_name for s in req_objs if s.skill_type == "REQUIRED"]
        job_pref = [s.normalized_skill or s.skill_name for s in req_objs if s.skill_type == "PREFERRED"]

        # Fallback to jd_intelligence if no JobSkillRequirement records exist
        if not job_req and job.jd_intelligence:
            job_req = job.jd_intelligence.get("required_skills", [])
            job_pref = job.jd_intelligence.get("preferred_skills", [])

        # 3. Match & Gap computation
        skill_match = SkillNormalizerService.match_skills(
            user_skills=norm_user_skills,
            job_required=job_req,
            job_preferred=job_pref,
        )

        priority_skills = skill_match["matched_required"] + skill_match["matched_preferred"]
        # Add remaining user skills as lower priority
        for s in norm_user_skills:
            if s not in priority_skills:
                priority_skills.append(s)

        missing_required = skill_match["missing_required"]
        missing_preferred = skill_match["missing_preferred"]

        # 4. Fetch relevant projects
        proj_res = await session.execute(
            select(Project).filter(Project.user_id == user_id)
        )
        projects = proj_res.scalars().all()
        relevant_projects = []
        req_set = set(SkillNormalizerService.normalize_list(job_req))

        for p in projects:
            techs = set(SkillNormalizerService.normalize_list(p.tech_stack or []))
            overlap = len(techs & req_set)
            relevant_projects.append({
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "tech_stack": p.tech_stack or [],
                "overlap_score": overlap,
            })
        relevant_projects.sort(key=lambda x: x["overlap_score"], reverse=True)

        # 5. Fetch relevant experiences
        exp_res = await session.execute(
            select(Experience).filter(Experience.user_id == user_id)
        )
        experiences = exp_res.scalars().all()
        relevant_experiences = []
        target_role_lower = (job.normalized_title or job.title or "").lower()

        for e in experiences:
            role_match = 1 if (e.role and e.role.lower() in target_role_lower or target_role_lower in (e.role or "").lower()) else 0
            relevant_experiences.append({
                "id": str(e.id),
                "company": e.company,
                "role": e.role,
                "achievements": e.achievements or [],
                "relevance_score": role_match,
            })
        relevant_experiences.sort(key=lambda x: x["relevance_score"], reverse=True)

        # 6. Sections to emphasize
        sections = ["Summary", "Skills", "Experience"]
        if relevant_projects:
            sections.append("Projects")

        plan = TailoringPlan(
            target_role=job.title,
            target_company=job.company,
            priority_skills=priority_skills,
            missing_required_skills=missing_required,
            missing_preferred_skills=missing_preferred,
            sections_to_emphasize=sections,
            relevant_projects=relevant_projects,
            relevant_experiences=relevant_experiences,
        )

        logger.info(f"TailoringPlanner: plan created. priority_skills={len(priority_skills)} missing_req={len(missing_required)}")
        return plan
