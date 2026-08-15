import uuid
import datetime
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.master_profile import MasterProfile, Education, Experience, Project, Certification, UserSkill, Evidence, CareerGoal
from app.repositories.graph_repository import PostgreSQLGraphRepository

logger = logging.getLogger("app.services.profile_manager")

class ProfileManager:
    """
    Service managing user profile career entities, skills, goals, evidence registration,
    and synchronizing them to the Knowledge Graph projection layer.
    """

    @staticmethod
    async def get_profile(session: AsyncSession, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Retrieves the complete, canonical profile details from relational tables.
        """
        # Fetch MasterProfile header
        query = select(MasterProfile).filter(MasterProfile.user_id == user_id)
        result = await session.execute(query)
        profile = result.scalars().first()

        if not profile:
            # Lazy initialize profile header
            profile = MasterProfile(user_id=user_id, personal_info={})
            session.add(profile)
            await session.flush()

        # Fetch educations
        q_edu = select(Education).filter(Education.user_id == user_id)
        r_edu = await session.execute(q_edu)
        educations = list(r_edu.scalars().all())

        # Fetch experiences
        q_exp = select(Experience).filter(Experience.user_id == user_id)
        r_exp = await session.execute(q_exp)
        experiences = list(r_exp.scalars().all())

        # Fetch projects
        q_proj = select(Project).filter(Project.user_id == user_id)
        r_proj = await session.execute(q_proj)
        projects = list(r_proj.scalars().all())

        # Fetch certifications
        q_cert = select(Certification).filter(Certification.user_id == user_id)
        r_cert = await session.execute(q_cert)
        certifications = list(r_cert.scalars().all())

        # Fetch skills
        q_skill = select(UserSkill).filter(UserSkill.user_id == user_id)
        r_skill = await session.execute(q_skill)
        skills = list(r_skill.scalars().all())

        # Fetch goals
        q_goal = select(CareerGoal).filter(CareerGoal.user_id == user_id)
        r_goal = await session.execute(q_goal)
        goals = r_goal.scalars().first()

        if not goals:
            # Lazy initialize career goals
            goals = CareerGoal(user_id=user_id)
            session.add(goals)
            await session.flush()

        return {
            "personal_info": profile.personal_info,
            "educations": [
                {
                    "id": str(e.id),
                    "school": e.school,
                    "degree": e.degree,
                    "field_of_study": e.field_of_study,
                    "start_date": e.start_date,
                    "end_date": e.end_date
                } for e in educations
            ],
            "experiences": [
                {
                    "id": str(exp.id),
                    "company": exp.company,
                    "role": exp.role,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "description": exp.description,
                    "achievements": exp.achievements
                } for exp in experiences
            ],
            "projects": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "description": p.description,
                    "url": p.url,
                    "technologies": p.technologies
                } for p in projects
            ],
            "certifications": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "issuing_organization": c.issuing_organization,
                    "issue_date": c.issue_date,
                    "expiration_date": c.expiration_date,
                    "credential_id": c.credential_id,
                    "credential_url": c.credential_url
                } for c in certifications
            ],
            "skills": [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "normalized_name": s.normalized_name,
                    "category": s.category,
                    "proficiency": s.proficiency,
                    "status": s.status,
                    "first_verified_at": s.first_verified_at.isoformat() if s.first_verified_at else None,
                    "last_verified_at": s.last_verified_at.isoformat() if s.last_verified_at else None,
                    "evidence": s.evidence
                } for s in skills
            ],
            "goals": {
                "target_roles": goals.target_roles,
                "target_salary": goals.target_salary,
                "target_locations": goals.target_locations,
                "preferred_companies": goals.preferred_companies,
                "preferred_industries": goals.preferred_industries,
                "work_mode": goals.work_mode,
                "career_level": goals.career_level,
                "application_preferences": goals.application_preferences
            }
        }

    @staticmethod
    async def update_personal_info(session: AsyncSession, user_id: uuid.UUID, info: Dict[str, Any]) -> MasterProfile:
        query = select(MasterProfile).filter(MasterProfile.user_id == user_id)
        result = await session.execute(query)
        profile = result.scalars().first()
        if not profile:
            profile = MasterProfile(user_id=user_id, personal_info=info)
            session.add(profile)
        else:
            profile.personal_info = info
        await session.flush()
        return profile

    @staticmethod
    async def upsert_education(session: AsyncSession, user_id: uuid.UUID, edu_data: Dict[str, Any]) -> Education:
        profile_query = select(MasterProfile).filter(MasterProfile.user_id == user_id)
        profile_res = await session.execute(profile_query)
        profile = profile_res.scalars().first()
        if not profile:
            profile = MasterProfile(user_id=user_id, personal_info={})
            session.add(profile)
            await session.flush()

        edu_id = edu_data.get("id")
        edu = None
        if edu_id:
            edu_query = select(Education).filter(Education.id == uuid.UUID(edu_id), Education.user_id == user_id)
            edu_res = await session.execute(edu_query)
            edu = edu_res.scalars().first()

        if not edu:
            edu = Education(
                user_id=user_id,
                profile_id=profile.id,
                school=edu_data["school"],
                degree=edu_data["degree"],
                field_of_study=edu_data["field_of_study"],
                start_date=edu_data.get("start_date"),
                end_date=edu_data.get("end_date")
            )
            session.add(edu)
        else:
            edu.school = edu_data["school"]
            edu.degree = edu_data["degree"]
            edu.field_of_study = edu_data["field_of_study"]
            edu.start_date = edu_data.get("start_date")
            edu.end_date = edu_data.get("end_date")

        await session.flush()
        return edu

    @staticmethod
    async def delete_education(session: AsyncSession, user_id: uuid.UUID, edu_id: uuid.UUID) -> None:
        q = delete(Education).filter(Education.id == edu_id, Education.user_id == user_id)
        await session.execute(q)
        await session.flush()

    @staticmethod
    async def upsert_experience(session: AsyncSession, user_id: uuid.UUID, exp_data: Dict[str, Any]) -> Experience:
        profile_query = select(MasterProfile).filter(MasterProfile.user_id == user_id)
        profile_res = await session.execute(profile_query)
        profile = profile_res.scalars().first()
        if not profile:
            profile = MasterProfile(user_id=user_id, personal_info={})
            session.add(profile)
            await session.flush()

        exp_id = exp_data.get("id")
        exp = None
        if exp_id:
            exp_query = select(Experience).filter(Experience.id == uuid.UUID(exp_id), Experience.user_id == user_id)
            exp_res = await session.execute(exp_query)
            exp = exp_res.scalars().first()

        if not exp:
            exp = Experience(
                user_id=user_id,
                profile_id=profile.id,
                company=exp_data["company"],
                role=exp_data["role"],
                start_date=exp_data.get("start_date"),
                end_date=exp_data.get("end_date"),
                description=exp_data.get("description"),
                achievements=exp_data.get("achievements", [])
            )
            session.add(exp)
        else:
            exp.company = exp_data["company"]
            exp.role = exp_data["role"]
            exp.start_date = exp_data.get("start_date")
            exp.end_date = exp_data.get("end_date")
            exp.description = exp_data.get("description")
            exp.achievements = exp_data.get("achievements", [])

        await session.flush()
        return exp

    @staticmethod
    async def delete_experience(session: AsyncSession, user_id: uuid.UUID, exp_id: uuid.UUID) -> None:
        q = delete(Experience).filter(Experience.id == exp_id, Experience.user_id == user_id)
        await session.execute(q)
        await session.flush()

    @staticmethod
    async def upsert_project(session: AsyncSession, user_id: uuid.UUID, proj_data: Dict[str, Any]) -> Project:
        profile_query = select(MasterProfile).filter(MasterProfile.user_id == user_id)
        profile_res = await session.execute(profile_query)
        profile = profile_res.scalars().first()
        if not profile:
            profile = MasterProfile(user_id=user_id, personal_info={})
            session.add(profile)
            await session.flush()

        proj_id = proj_data.get("id")
        proj = None
        if proj_id:
            proj_query = select(Project).filter(Project.id == uuid.UUID(proj_id), Project.user_id == user_id)
            proj_res = await session.execute(proj_query)
            proj = proj_res.scalars().first()

        if not proj:
            proj = Project(
                user_id=user_id,
                profile_id=profile.id,
                name=proj_data["name"],
                description=proj_data.get("description"),
                url=proj_data.get("url"),
                technologies=proj_data.get("technologies", [])
            )
            session.add(proj)
        else:
            proj.name = proj_data["name"]
            proj.description = proj_data.get("description")
            proj.url = proj_data.get("url")
            proj.technologies = proj_data.get("technologies", [])

        await session.flush()
        return proj

    @staticmethod
    async def delete_project(session: AsyncSession, user_id: uuid.UUID, proj_id: uuid.UUID) -> None:
        q = delete(Project).filter(Project.id == proj_id, Project.user_id == user_id)
        await session.execute(q)
        await session.flush()

    @staticmethod
    async def upsert_certification(session: AsyncSession, user_id: uuid.UUID, cert_data: Dict[str, Any]) -> Certification:
        profile_query = select(MasterProfile).filter(MasterProfile.user_id == user_id)
        profile_res = await session.execute(profile_query)
        profile = profile_res.scalars().first()
        if not profile:
            profile = MasterProfile(user_id=user_id, personal_info={})
            session.add(profile)
            await session.flush()

        cert_id = cert_data.get("id")
        cert = None
        if cert_id:
            cert_query = select(Certification).filter(Certification.id == uuid.UUID(cert_id), Certification.user_id == user_id)
            cert_res = await session.execute(cert_query)
            cert = cert_res.scalars().first()

        if not cert:
            cert = Certification(
                user_id=user_id,
                profile_id=profile.id,
                name=cert_data["name"],
                issuing_organization=cert_data["issuing_organization"],
                issue_date=cert_data.get("issue_date"),
                expiration_date=cert_data.get("expiration_date"),
                credential_id=cert_data.get("credential_id"),
                credential_url=cert_data.get("credential_url")
            )
            session.add(cert)
        else:
            cert.name = cert_data["name"]
            cert.issuing_organization = cert_data["issuing_organization"]
            cert.issue_date = cert_data.get("issue_date")
            cert.expiration_date = cert_data.get("expiration_date")
            cert.credential_id = cert_data.get("credential_id")
            cert.credential_url = cert_data.get("credential_url")

        await session.flush()
        return cert

    @staticmethod
    async def delete_certification(session: AsyncSession, user_id: uuid.UUID, cert_id: uuid.UUID) -> None:
        q = delete(Certification).filter(Certification.id == cert_id, Certification.user_id == user_id)
        await session.execute(q)
        await session.flush()

    @staticmethod
    async def add_user_skill(
        session: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        category: str = "general",
        proficiency: str = "Intermediate",
        status: str = "USER_PROVIDED",
        evidence_ids: List[str] = None
    ) -> UserSkill:
        normalized = name.strip().lower()
        
        # Check if skill exists
        query = select(UserSkill).filter(UserSkill.user_id == user_id, UserSkill.normalized_name == normalized)
        res = await session.execute(query)
        skill = res.scalars().first()

        now = datetime.datetime.utcnow()
        verified_at = now if status == "VERIFIED" else None

        if not skill:
            skill = UserSkill(
                user_id=user_id,
                name=name,
                normalized_name=normalized,
                category=category,
                proficiency=proficiency,
                status=status,
                first_verified_at=verified_at,
                last_verified_at=verified_at,
                evidence=evidence_ids or []
            )
            session.add(skill)
        else:
            # Rule promotion: AI_INFERRED -> USER REVIEW -> USER APPROVES -> USER_PROVIDED / VERIFIED
            # So if someone tries to overwrite, don't auto-verify unless explicit
            skill.proficiency = proficiency
            skill.category = category
            
            # If changing status to verified, log timestamp
            if status == "VERIFIED" and skill.status != "VERIFIED":
                skill.first_verified_at = skill.first_verified_at or now
                skill.last_verified_at = now
            skill.status = status
            if evidence_ids:
                skill.evidence = list(set(skill.evidence + evidence_ids))

        await session.flush()
        return skill

    @staticmethod
    async def update_user_skill_status(session: AsyncSession, user_id: uuid.UUID, skill_id: uuid.UUID, status: str) -> Optional[UserSkill]:
        query = select(UserSkill).filter(UserSkill.id == skill_id, UserSkill.user_id == user_id)
        res = await session.execute(query)
        skill = res.scalars().first()
        if skill:
            now = datetime.datetime.utcnow()
            if status == "VERIFIED" and skill.status != "VERIFIED":
                skill.first_verified_at = skill.first_verified_at or now
                skill.last_verified_at = now
            skill.status = status
            await session.flush()
        return skill

    @staticmethod
    async def delete_user_skill(session: AsyncSession, user_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        q = delete(UserSkill).filter(UserSkill.id == skill_id, UserSkill.user_id == user_id)
        await session.execute(q)
        await session.flush()

    @staticmethod
    async def add_evidence(
        session: AsyncSession,
        user_id: uuid.UUID,
        evidence_type: str,
        description: str,
        source_url: Optional[str] = None,
        properties: Optional[dict] = None
    ) -> Evidence:
        evidence = Evidence(
            user_id=user_id,
            type=evidence_type,
            source_url=source_url,
            description=description,
            properties=properties or {}
        )
        session.add(evidence)
        await session.flush()
        return evidence

    @staticmethod
    async def update_goals(session: AsyncSession, user_id: uuid.UUID, goals_data: Dict[str, Any]) -> CareerGoal:
        query = select(CareerGoal).filter(CareerGoal.user_id == user_id)
        result = await session.execute(query)
        goals = result.scalars().first()

        if not goals:
            goals = CareerGoal(
                user_id=user_id,
                target_roles=goals_data.get("target_roles", []),
                target_salary=goals_data.get("target_salary"),
                target_locations=goals_data.get("target_locations", []),
                preferred_companies=goals_data.get("preferred_companies", []),
                preferred_industries=goals_data.get("preferred_industries", []),
                work_mode=goals_data.get("work_mode", "Remote"),
                career_level=goals_data.get("career_level", "Mid"),
                application_preferences=goals_data.get("application_preferences", {})
            )
            session.add(goals)
        else:
            goals.target_roles = goals_data.get("target_roles", goals.target_roles)
            goals.target_salary = goals_data.get("target_salary", goals.target_salary)
            goals.target_locations = goals_data.get("target_locations", goals.target_locations)
            goals.preferred_companies = goals_data.get("preferred_companies", goals.preferred_companies)
            goals.preferred_industries = goals_data.get("preferred_industries", goals.preferred_industries)
            goals.work_mode = goals_data.get("work_mode", goals.work_mode)
            goals.career_level = goals_data.get("career_level", goals.career_level)
            goals.application_preferences = goals_data.get("application_preferences", goals.application_preferences)

        await session.flush()
        return goals

    @staticmethod
    async def sync_graph_projection(session: AsyncSession, user_id: uuid.UUID) -> None:
        """
        Synchronizes database profile records to the derived Knowledge Graph projection layer.
        """
        logger.info(f"Syncing Knowledge Graph projection for user {user_id}")
        graph_repo = PostgreSQLGraphRepository(session)
        user_node_id = f"user:{user_id}"

        # Fetch profile
        q_profile = select(MasterProfile).filter(MasterProfile.user_id == user_id)
        profile = (await session.execute(q_profile)).scalars().first()
        name = "User"
        email = ""
        if profile and profile.personal_info:
            name = profile.personal_info.get("name", "User")
            email = profile.personal_info.get("email", "")

        await graph_repo.add_entity_node(
            node_id=user_node_id,
            entity_type="USER",
            properties={"name": name, "email": email}
        )

        # Sync skills
        q_skills = select(UserSkill).filter(UserSkill.user_id == user_id)
        skills = (await session.execute(q_skills)).scalars().all()
        for s in skills:
            skill_node_id = f"skill:{s.normalized_name.replace(' ', '_')}"
            await graph_repo.add_entity_node(
                node_id=skill_node_id,
                entity_type="SKILL",
                properties={"name": s.name, "category": s.category, "status": s.status}
            )
            await graph_repo.add_relationship(
                source_id=user_node_id,
                target_id=skill_node_id,
                relation_type="HAS_SKILL",
                properties={"proficiency": s.proficiency, "status": s.status}
            )

        # Sync experience
        q_exp = select(Experience).filter(Experience.user_id == user_id)
        exps = (await session.execute(q_exp)).scalars().all()
        for e in exps:
            company_node_id = f"company:{e.company.lower().replace(' ', '_')}"
            await graph_repo.add_entity_node(
                node_id=company_node_id,
                entity_type="COMPANY",
                properties={"name": e.company}
            )
            await graph_repo.add_relationship(
                source_id=user_node_id,
                target_id=company_node_id,
                relation_type="WORKED_AT",
                properties={"role": e.role, "start": e.start_date, "end": e.end_date}
            )
            
        # Sync projects
        q_proj = select(Project).filter(Project.user_id == user_id)
        projs = (await session.execute(q_proj)).scalars().all()
        for p in projs:
            proj_node_id = f"project:{p.name.lower().replace(' ', '_')}"
            await graph_repo.add_entity_node(
                node_id=proj_node_id,
                entity_type="PROJECT",
                properties={"name": p.name, "description": p.description}
            )
            await graph_repo.add_relationship(
                source_id=user_node_id,
                target_id=proj_node_id,
                relation_type="BUILT",
                properties={"technologies": p.technologies}
            )
            
        # Sync certifications
        q_cert = select(Certification).filter(Certification.user_id == user_id)
        certs = (await session.execute(q_cert)).scalars().all()
        for c in certs:
            cert_node_id = f"certification:{c.name.lower().replace(' ', '_')}"
            await graph_repo.add_entity_node(
                node_id=cert_node_id,
                entity_type="CERTIFICATION",
                properties={"name": c.name, "issuer": c.issuing_organization}
            )
            await graph_repo.add_relationship(
                source_id=user_node_id,
                target_id=cert_node_id,
                relation_type="HAS_CERTIFICATION",
                properties={"issue_date": c.issue_date}
            )
            
        # Sync evidence
        q_ev = select(Evidence).filter(Evidence.user_id == user_id)
        evs = (await session.execute(q_ev)).scalars().all()
        for ev in evs:
            ev_node_id = f"evidence:{str(ev.id)}"
            await graph_repo.add_entity_node(
                node_id=ev_node_id,
                entity_type="EVIDENCE",
                properties={"type": ev.type, "description": ev.description}
            )
            await graph_repo.add_relationship(
                source_id=user_node_id,
                target_id=ev_node_id,
                relation_type="HAS_EVIDENCE",
                properties={"url": ev.source_url}
            )
