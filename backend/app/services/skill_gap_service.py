"""
SkillGapService — Evaluates job skill gaps and aggregates market skill gap frequencies.

NON-NEGOTIABLE INVARIANTS:
1. Missing skills MUST NEVER be automatically inserted into UserSkill or master profile data.
2. Missing skills remain skill gaps for learning priorities only.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job import JobPosting
from app.models.job_intelligence import JobSkillRequirement
from app.models.master_profile import MasterProfile, UserSkill
from app.models.job_discovery import SkillGapAggregate
from app.services.skill_normalizer import SkillNormalizerService

logger = logging.getLogger("app.services.skill_gap")


class SkillGapService:
    """
    Evaluates individual job skill gaps and manages aggregate market skill gap metrics.
    """

    @staticmethod
    async def evaluate_job_skill_gaps(
        session: AsyncSession,
        user: User,
        job: JobPosting
    ) -> Dict[str, Any]:
        # Fetch verified candidate skills
        p_res = await session.execute(select(MasterProfile).filter(MasterProfile.user_id == user.id))
        profile = p_res.scalars().first()

        user_skills_clean = set()
        if profile:
            sk_res = await session.execute(select(UserSkill).filter(UserSkill.profile_id == profile.id))
            for sk in sk_res.scalars().all():
                norm = SkillNormalizerService.normalize(sk.name)
                user_skills_clean.add(norm)

        # Fetch job skill requirements
        req_res = await session.execute(
            select(JobSkillRequirement).filter(JobSkillRequirement.job_id == job.id)
        )
        job_reqs = req_res.scalars().all()

        matched = []
        missing_required = []
        missing_preferred = []

        for req in job_reqs:
            norm_name = SkillNormalizerService.normalize(req.skill_name)
            is_present = norm_name in user_skills_clean

            if is_present:
                matched.append(req.skill_name)
            else:
                if req.importance == "REQUIRED":
                    missing_required.append(req.skill_name)
                else:
                    missing_preferred.append(req.skill_name)

        return {
            "matched_skills": matched,
            "missing_required_skills": missing_required,
            "missing_preferred_skills": missing_preferred,
            "matched_count": len(matched),
            "missing_required_count": len(missing_required),
            "missing_preferred_count": len(missing_preferred),
        }

    @staticmethod
    async def aggregate_market_skill_gaps(
        session: AsyncSession,
        user: User
    ) -> List[Dict[str, Any]]:
        """
        Aggregates missing skill frequencies across candidate jobs.
        Updates SkillGapAggregate DB records.
        """
        res = await session.execute(
            select(SkillGapAggregate).filter(SkillGapAggregate.user_id == user.id).order_by(SkillGapAggregate.job_count.desc())
        )
        aggregates = res.scalars().all()

        result = []
        for agg in aggregates:
            # Learning priority formula: job_count * 5.0 + required_count * 2.0 + importance_score
            prio = round(agg.job_count * 5.0 + agg.required_count * 2.0 + agg.importance_score, 1)
            agg.learning_priority = prio
            result.append({
                "skill_name": agg.skill_name,
                "job_count": agg.job_count,
                "required_count": agg.required_count,
                "preferred_count": agg.preferred_count,
                "importance_score": agg.importance_score,
                "learning_priority": prio,
                "target_roles": agg.target_roles or [],
                "recommendation": f"Learning {agg.skill_name} unlocks {agg.job_count} target jobs (required in {agg.required_count})."
            })

        await session.commit()
        return result

    @staticmethod
    async def record_skill_gap_occurrence(
        session: AsyncSession,
        user: User,
        skill_name: str,
        is_required: bool = True,
        role_name: str = None
    ) -> None:
        """
        Records a single skill gap occurrence into SkillGapAggregate.
        INVARIANT: Does NOT create or touch UserSkill.
        """
        s_clean = skill_name.strip().title()
        res = await session.execute(
            select(SkillGapAggregate).filter(
                SkillGapAggregate.user_id == user.id,
                SkillGapAggregate.skill_name == s_clean
            )
        )
        agg = res.scalars().first()

        if not agg:
            agg = SkillGapAggregate(
                id=uuid.uuid4(),
                user_id=user.id,
                skill_name=s_clean,
                job_count=1,
                required_count=1 if is_required else 0,
                preferred_count=0 if is_required else 1,
                importance_score=10.0 if is_required else 5.0,
                learning_priority=15.0 if is_required else 10.0,
                target_roles=[role_name] if role_name else []
            )
            session.add(agg)
        else:
            agg.job_count += 1
            if is_required:
                agg.required_count += 1
            else:
                agg.preferred_count += 1
            if role_name and role_name not in (agg.target_roles or []):
                roles = list(agg.target_roles or [])
                roles.append(role_name)
                agg.target_roles = roles

        await session.commit()
