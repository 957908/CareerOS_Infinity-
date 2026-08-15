import uuid
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.master_profile import MasterProfile, Education, Experience, Project, Certification, UserSkill, Evidence, CareerGoal

logger = logging.getLogger("app.services.truth_guard")

class TruthGuard:
    """
    TruthGuard validates claims against canonical verified career data and
    linked evidence in PostgreSQL.
    """

    @staticmethod
    async def validate_claim(
        session: AsyncSession,
        user_id: uuid.UUID,
        claim_type: str,
        claim_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validates a single claim against canonical PostgreSQL state.
        Returns:
            dict containing: allowed (bool), reason (str), evidence_ids (list),
                            confidence (float), claim_type (str), validation_status (str)
        """
        logger.info(f"Validating claim: {claim_type} for user {user_id}")
        
        # Default response structure
        response = {
            "allowed": False,
            "reason": "Unknown claim type",
            "evidence_ids": [],
            "confidence": 1.0,
            "claim_type": claim_type,
            "validation_status": "REJECTED"
        }

        if claim_type == "SKILL":
            skill_name = claim_content.get("name", "").strip().lower()
            if not skill_name:
                response["reason"] = "Empty skill name claim"
                return response

            query = select(UserSkill).filter(
                UserSkill.user_id == user_id,
                UserSkill.normalized_name == skill_name
            )
            result = await session.execute(query)
            skill = result.scalars().first()

            if not skill:
                response["reason"] = f"No record found for skill: {claim_content.get('name')}"
                return response

            # Check status logic: Only USER_PROVIDED or VERIFIED are allowed.
            if skill.status not in ["VERIFIED", "USER_PROVIDED"]:
                response["reason"] = f"Skill {skill.name} has unverified status: {skill.status}"
                response["validation_status"] = "PENDING_VERIFICATION"
                return response

            # Success path
            response["allowed"] = True
            response["reason"] = f"Verified skill claim: {skill.name}"
            response["evidence_ids"] = skill.evidence
            response["validation_status"] = "VERIFIED"
            response["confidence"] = 1.0

        elif claim_type == "EXPERIENCE":
            company = claim_content.get("company", "").strip().lower()
            role = claim_content.get("role", "").strip().lower()
            if not company or not role:
                response["reason"] = "Company and role must be provided for experience verification"
                return response

            query = select(Experience).filter(
                Experience.user_id == user_id,
                Experience.company.ilike(company),
                Experience.role.ilike(role)
            )
            result = await session.execute(query)
            exp = result.scalars().first()

            if not exp:
                response["reason"] = f"No verified work experience found at {claim_content.get('company')} as {claim_content.get('role')}"
                return response

            # Checked description/achievements overlap
            achievement = claim_content.get("achievement", "")
            if achievement:
                overlap = False
                for canonical_ach in exp.achievements:
                    if achievement.lower() in canonical_ach.lower():
                        overlap = True
                        break
                if not overlap:
                    response["reason"] = f"Achievement text was not found in canonical profile records for role at {exp.company}"
                    return response

            response["allowed"] = True
            response["reason"] = f"Verified experience claim: {exp.role} at {exp.company}"
            response["validation_status"] = "VERIFIED"
            response["confidence"] = 0.95

        elif claim_type == "PROJECT":
            project_name = claim_content.get("name", "").strip().lower()
            if not project_name:
                response["reason"] = "Project name is required"
                return response

            query = select(Project).filter(
                Project.user_id == user_id,
                Project.name.ilike(project_name)
            )
            result = await session.execute(query)
            proj = result.scalars().first()

            if not proj:
                response["reason"] = f"No verified project found with name: {claim_content.get('name')}"
                return response

            response["allowed"] = True
            response["reason"] = f"Verified project claim: {proj.name}"
            response["validation_status"] = "VERIFIED"
            response["confidence"] = 0.95

        elif claim_type == "CERTIFICATION":
            cert_name = claim_content.get("name", "").strip().lower()
            if not cert_name:
                response["reason"] = "Certification name is required"
                return response

            query = select(Certification).filter(
                Certification.user_id == user_id,
                Certification.name.ilike(cert_name)
            )
            result = await session.execute(query)
            cert = result.scalars().first()

            if not cert:
                response["reason"] = f"No verified certification found with name: {claim_content.get('name')}"
                return response

            response["allowed"] = True
            response["reason"] = f"Verified certification claim: {cert.name}"
            response["validation_status"] = "VERIFIED"
            response["confidence"] = 0.95

        elif claim_type == "EDUCATION":
            school = claim_content.get("school", "").strip().lower()
            if not school:
                response["reason"] = "School name is required"
                return response

            query = select(Education).filter(
                Education.user_id == user_id,
                Education.school.ilike(school)
            )
            result = await session.execute(query)
            edu = result.scalars().first()

            if not edu:
                response["reason"] = f"No education record found at school: {claim_content.get('school')}"
                return response

            response["allowed"] = True
            response["reason"] = f"Verified education claim at {edu.school}"
            response["validation_status"] = "VERIFIED"
            response["confidence"] = 0.95

        elif claim_type == "PROFILE":
            query = select(MasterProfile).filter(MasterProfile.user_id == user_id)
            result = await session.execute(query)
            profile = result.scalars().first()
            if not profile:
                response["reason"] = "No master profile header found in PostgreSQL database."
                return response
            response["allowed"] = True
            response["reason"] = "Verified master profile header claim."
            response["validation_status"] = "VERIFIED"
            response["confidence"] = 1.0

        elif claim_type == "EVIDENCE":
            desc = claim_content.get("description", "").strip().lower()
            query = select(Evidence).filter(
                Evidence.user_id == user_id,
                Evidence.description.ilike(desc)
            )
            result = await session.execute(query)
            evidence = result.scalars().first()
            if not evidence:
                response["reason"] = f"No evidence registry record found matching description: {claim_content.get('description')}"
                return response
            response["allowed"] = True
            response["reason"] = f"Verified evidence registry claim: {evidence.description}"
            response["validation_status"] = "VERIFIED"
            response["confidence"] = 1.0

        elif claim_type == "GOAL":
            title = claim_content.get("title", "").strip().lower()
            query = select(CareerGoal).filter(
                CareerGoal.user_id == user_id,
                CareerGoal.title.ilike(title)
            )
            result = await session.execute(query)
            goal = result.scalars().first()
            if not goal:
                response["reason"] = f"No career goal record found matching title: {claim_content.get('title')}"
                return response
            response["allowed"] = True
            response["reason"] = f"Verified career goal claim: {goal.title}"
            response["validation_status"] = "VERIFIED"
            response["confidence"] = 1.0

        return response
