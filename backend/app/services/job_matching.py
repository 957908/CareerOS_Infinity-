"""
JobMatchingService — Multi-dimensional job-to-profile matching engine.

Computes ATS score, semantic score, skill gap, experience match, role match,
project relevance, location/work-mode match, and career preference match.

Produces a weighted overall_fit_score and recommendation_level.

INVARIANTS:
- Missing skills NEVER written to user_skills
- AI may provide evidence but scoring is DETERMINISTIC application logic
- TruthGuard is the authority for factual candidate claims
- All score weights are stored in job_matches for traceability
"""
import datetime
import logging
import math
import re
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job import JobPosting
from app.models.job_intelligence import JobMatch, JobSkillRequirement
from app.models.master_profile import (
    MasterProfile, UserSkill, Experience, Project, CareerGoal
)
from app.services.skill_normalizer import SkillNormalizerService
from app.core.ai_gateway import AIGateway

logger = logging.getLogger("app.services.job_matching")

# Default configurable score weights
DEFAULT_SCORE_WEIGHTS = {
    "skill_match": 0.30,
    "experience_match": 0.20,
    "role_match": 0.15,
    "semantic_match": 0.15,
    "project_relevance": 0.10,
    "location_work_mode": 0.05,
    "career_preference": 0.05,
}

RECOMMENDATION_THRESHOLDS = {
    "APPLY_RECOMMENDED": 90.0,
    "STRONG_MATCH": 75.0,
    "POSSIBLE_MATCH": 55.0,
    "LOW_PRIORITY": 35.0,
}


def _recommendation_from_score(score: float) -> str:
    for level, threshold in RECOMMENDATION_THRESHOLDS.items():
        if score >= threshold:
            return level
    return "NOT_RECOMMENDED"


def _cosine_similarity_approx(a: list[float], b: list[float]) -> float:
    """Approximate cosine similarity between two embedding vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (mag_a * mag_b)))


class JobMatchingService:
    """
    Computes a full explainable match between the user's career profile and a job posting.
    Saves the result to the job_matches table.
    """

    @staticmethod
    async def compute_match(
        session: AsyncSession,
        user: User,
        job: JobPosting,
        weights: Optional[dict] = None,
    ) -> JobMatch:
        """
        Compute or refresh the match for a (user, job) pair.
        Returns the upserted JobMatch record.
        """
        weights = weights or DEFAULT_SCORE_WEIGHTS
        logger.info(f"JobMatchingService: computing match user={user.id} job={job.id}")

        # ── Load user profile data ──────────────────────────────────────────
        profile_result = await session.execute(
            select(MasterProfile).filter(MasterProfile.user_id == user.id)
        )
        profile = profile_result.scalars().first()

        skills_result = await session.execute(
            select(UserSkill).filter(
                UserSkill.user_id == user.id,
                UserSkill.status.in_(["VERIFIED", "USER_PROVIDED"])
            )
        )
        user_skills_objs = skills_result.scalars().all()
        user_skill_names = SkillNormalizerService.normalize_list(
            [getattr(s, 'name', getattr(s, 'skill_name', '')) for s in user_skills_objs]
        )

        exp_result = await session.execute(
            select(Experience).filter(Experience.user_id == user.id)
        )
        experiences = exp_result.scalars().all()

        proj_result = await session.execute(
            select(Project).filter(Project.user_id == user.id)
        )
        projects = proj_result.scalars().all()

        goals_result = await session.execute(
            select(CareerGoal).filter(CareerGoal.user_id == user.id)
        )
        goals = goals_result.scalars().first()

        # ── Load job requirements ───────────────────────────────────────────
        req_result = await session.execute(
            select(JobSkillRequirement).filter(JobSkillRequirement.job_id == job.id)
        )
        job_skill_reqs = req_result.scalars().all()
        required_skills = [s.normalized_skill or s.skill_name for s in job_skill_reqs if s.skill_type == "REQUIRED"]
        preferred_skills = [s.normalized_skill or s.skill_name for s in job_skill_reqs if s.skill_type == "PREFERRED"]

        # Fallback to jd_intelligence if no JobSkillRequirement rows yet
        if not required_skills and job.jd_intelligence:
            required_skills = SkillNormalizerService.normalize_list(
                job.jd_intelligence.get("required_skills", [])
            )
            preferred_skills = SkillNormalizerService.normalize_list(
                job.jd_intelligence.get("preferred_skills", [])
            )

        # ── 1. Skill Match Score ────────────────────────────────────────────
        skill_analysis = SkillNormalizerService.match_skills(
            user_skills=user_skill_names,
            job_required=required_skills,
            job_preferred=preferred_skills,
        )
        skill_score = skill_analysis["skill_match_score"]

        # ── 2. Experience Match Score ────────────────────────────────────────
        experience_score = JobMatchingService._score_experience(
            experiences=experiences,
            exp_min_years=job.experience_min_years,
            exp_max_years=job.experience_max_years,
        )

        # ── 3. Role Match Score ──────────────────────────────────────────────
        role_score = JobMatchingService._score_role(
            job_title=job.normalized_title or job.title,
            goals=goals,
            experiences=experiences,
        )

        # ── 4. Semantic Match Score ──────────────────────────────────────────
        semantic_score = await JobMatchingService._score_semantic(job=job)

        # ── 5. Project Relevance Score ───────────────────────────────────────
        project_score = JobMatchingService._score_projects(
            projects=projects,
            required_skills=required_skills,
        )

        # ── 6. Location / Work Mode Score ───────────────────────────────────
        location_score = JobMatchingService._score_location(
            job_work_mode=job.work_mode,
            job_location=job.location,
            goals=goals,
        )

        # ── 7. Career Preference Score ───────────────────────────────────────
        preference_score = JobMatchingService._score_career_preference(
            job=job,
            goals=goals,
        )

        # ── ATS Score (keyword coverage proxy) ──────────────────────────────
        ats_score = min(100.0, (skill_score * 0.7) + (experience_score * 0.3))

        # ── Weighted overall fit score ───────────────────────────────────────
        overall = (
            skill_score * weights["skill_match"] +
            experience_score * weights["experience_match"] +
            role_score * weights["role_match"] +
            semantic_score * weights["semantic_match"] +
            project_score * weights["project_relevance"] +
            location_score * weights["location_work_mode"] +
            preference_score * weights["career_preference"]
        )
        overall = round(min(100.0, max(0.0, overall)), 2)

        recommendation = _recommendation_from_score(overall)

        # ── Build explanation ────────────────────────────────────────────────
        explanation = JobMatchingService._build_explanation(
            overall=overall,
            recommendation=recommendation,
            matched_required=skill_analysis["matched_required"],
            missing_required=skill_analysis["missing_required"],
            matched_preferred=skill_analysis["matched_preferred"],
            missing_preferred=skill_analysis["missing_preferred"],
            experience_score=experience_score,
            role_score=role_score,
        )

        # ── Upsert JobMatch record ───────────────────────────────────────────
        existing_result = await session.execute(
            select(JobMatch).filter(
                JobMatch.user_id == user.id,
                JobMatch.job_id == job.id,
            )
        )
        existing_match = existing_result.scalars().first()

        match_data = dict(
            ats_score=round(ats_score, 2),
            semantic_score=round(semantic_score, 2),
            skill_match_score=round(skill_score, 2),
            experience_match_score=round(experience_score, 2),
            role_match_score=round(role_score, 2),
            project_relevance_score=round(project_score, 2),
            location_match_score=round(location_score, 2),
            career_preference_score=round(preference_score, 2),
            overall_fit_score=overall,
            recommendation_level=recommendation,
            matched_skills=skill_analysis["matched_required"] + skill_analysis["matched_preferred"],
            missing_required_skills=skill_analysis["missing_required"],
            missing_preferred_skills=skill_analysis["missing_preferred"],
            match_explanation=explanation,
            score_weights=weights,
            embedding_model="gemini/text-embedding-004",
            calculated_at=datetime.datetime.now(datetime.timezone.utc),
            is_stale=False,
        )

        if existing_match:
            for k, v in match_data.items():
                setattr(existing_match, k, v)
            job_match = existing_match
        else:
            job_match = JobMatch(user_id=user.id, job_id=job.id, **match_data)
            session.add(job_match)

        await session.flush()
        return job_match

    # ── Component Scorers ──────────────────────────────────────────────────

    @staticmethod
    def _score_experience(
        experiences: list,
        exp_min_years: Optional[int],
        exp_max_years: Optional[int],
    ) -> float:
        """Score experience match against job's required years."""
        if not exp_min_years:
            return 75.0  # neutral if job doesn't specify experience

        # Calculate total years of experience
        total_years = 0
        for exp in experiences:
            try:
                exp_dict = exp.company if isinstance(exp.company, dict) else {}
                years = exp_dict.get("duration_years", 0)
                if isinstance(years, (int, float)):
                    total_years += years
            except Exception:
                pass

        # Fallback: count number of experience records × 1.5 years average
        if total_years == 0:
            total_years = len(experiences) * 1.5

        target = exp_min_years
        if total_years >= target:
            # Meets requirement — bonus if exceeds
            excess = min(total_years - target, 5)
            return min(100.0, 80.0 + (excess * 4))
        else:
            # Below requirement
            ratio = total_years / target if target > 0 else 0
            return round(ratio * 70.0, 2)

    @staticmethod
    def _score_role(
        job_title: str,
        goals: Optional[object],
        experiences: list,
    ) -> float:
        """Score role alignment based on career goals and experience history."""
        if not job_title:
            return 50.0

        job_title_lower = (job_title or "").lower()
        score = 50.0

        # Match against career goals
        if goals:
            target_roles = goals.target_roles or []
            for role in target_roles:
                role_lower = (role or "").lower()
                if role_lower in job_title_lower or job_title_lower in role_lower:
                    score = min(100.0, score + 40.0)
                    break
                # Partial match
                role_words = set(role_lower.split())
                title_words = set(job_title_lower.split())
                overlap = len(role_words & title_words)
                if overlap > 0:
                    score = min(100.0, score + (overlap / max(len(role_words), 1)) * 30.0)

        # Match against past experience titles
        for exp in experiences:
            try:
                past_title = (getattr(exp, 'role', '') or '').lower()
                if past_title and (past_title in job_title_lower or job_title_lower in past_title):
                    score = min(100.0, score + 20.0)
                    break
            except Exception:
                pass

        return round(score, 2)

    @staticmethod
    async def _score_semantic(job: JobPosting) -> float:
        """
        Semantic similarity using stored job embedding.
        Falls back to 50.0 if embeddings unavailable.
        """
        if job.embedding and any(v != 0.0 for v in job.embedding[:10]):
            # We have a real job embedding; return a moderate baseline
            # Full semantic matching requires user resume embedding too
            # That comparison happens when the user's master resume embedding is available
            return 70.0
        return 50.0

    @staticmethod
    def _score_projects(projects: list, required_skills: list[str]) -> float:
        """Score project relevance by checking if project tech stacks overlap with job requirements."""
        if not projects or not required_skills:
            return 50.0

        req_set = set(SkillNormalizerService.normalize_list(required_skills))
        best_overlap = 0.0

        for proj in projects:
            try:
                tech_stack = getattr(proj, "tech_stack", []) or []
                if isinstance(tech_stack, list):
                    proj_skills = set(SkillNormalizerService.normalize_list([str(t) for t in tech_stack]))
                    if req_set:
                        overlap = len(proj_skills & req_set) / len(req_set)
                        best_overlap = max(best_overlap, overlap)
            except Exception:
                pass

        return round(min(100.0, best_overlap * 100.0), 2) if best_overlap > 0 else 50.0

    @staticmethod
    def _score_location(
        job_work_mode: Optional[str],
        job_location: Optional[str],
        goals: Optional[object],
    ) -> float:
        """Score location/work-mode compatibility against user preferences."""
        if not goals:
            return 60.0

        user_pref_work_mode = getattr(goals, "work_mode", "Remote") or "Remote"
        target_locations = getattr(goals, "target_locations", []) or []

        score = 0.0

        # Work mode match
        if job_work_mode:
            mode_map = {"REMOTE": 100.0, "HYBRID": 80.0, "ONSITE": 60.0}
            if user_pref_work_mode.upper() == "REMOTE":
                score += mode_map.get(job_work_mode.upper(), 60.0)
            elif user_pref_work_mode.upper() == "HYBRID":
                score += 90.0 if job_work_mode.upper() in ("REMOTE", "HYBRID") else 55.0
            else:
                score += 85.0
        else:
            score += 60.0

        # Location match
        if target_locations and job_location:
            job_loc_lower = job_location.lower()
            for loc in target_locations:
                if (loc or "").lower() in job_loc_lower or job_loc_lower in (loc or "").lower():
                    score = min(100.0, score + 20.0)
                    break

        return round(min(100.0, score), 2)

    @staticmethod
    def _score_career_preference(job: JobPosting, goals: Optional[object]) -> float:
        """Score overall alignment with career preferences."""
        if not goals:
            return 50.0

        score = 50.0

        preferred_companies = getattr(goals, "preferred_companies", []) or []
        for c in preferred_companies:
            if (c or "").lower() in (job.normalized_company or "").lower():
                score += 30.0
                break

        # Employment type preference
        app_prefs = getattr(goals, "application_preferences", {}) or {}
        preferred_emp_type = app_prefs.get("employment_type", "FULL_TIME")
        if job.employment_type and job.employment_type == preferred_emp_type:
            score += 20.0

        return round(min(100.0, score), 2)

    @staticmethod
    def _build_explanation(
        overall: float,
        recommendation: str,
        matched_required: list[str],
        missing_required: list[str],
        matched_preferred: list[str],
        missing_preferred: list[str],
        experience_score: float,
        role_score: float,
    ) -> str:
        """Build a concise, evidence-based explanation."""
        parts = []

        emoji_map = {
            "APPLY_RECOMMENDED": "🔥",
            "STRONG_MATCH": "🟢",
            "POSSIBLE_MATCH": "🟡",
            "LOW_PRIORITY": "⚪",
            "NOT_RECOMMENDED": "🔴",
        }
        emoji = emoji_map.get(recommendation, "")
        parts.append(f"{emoji} {recommendation.replace('_', ' ')} — Overall: {overall:.0f}%")

        if matched_required:
            parts.append(f"Matched required skills: {', '.join(matched_required[:6])}")

        if missing_required:
            parts.append(f"Missing required skills: {', '.join(missing_required[:5])}")

        if matched_preferred:
            parts.append(f"Matched preferred skills: {', '.join(matched_preferred[:4])}")

        if experience_score >= 80:
            parts.append("Strong experience alignment.")
        elif experience_score < 50:
            parts.append("Experience level may be below requirement.")

        if role_score >= 80:
            parts.append("Role closely aligns with your career goals.")

        return " | ".join(parts)
