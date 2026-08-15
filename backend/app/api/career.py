import uuid
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.profile_manager import ProfileManager

logger = logging.getLogger("app.api.career")
router = APIRouter(prefix="/career", tags=["Career Operating System"])

@router.get("/profile", status_code=status.HTTP_200_OK)
async def get_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Retrieves the Master Profile, education, experience, projects, certifications,
    skills list and career goals.
    """
    try:
        profile_data = await ProfileManager.get_profile(session, current_user.id)
        return profile_data
    except Exception as e:
        logger.error(f"Failed to fetch profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error fetching career profile")

@router.put("/profile", status_code=status.HTTP_200_OK)
async def update_personal_info(
    info: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Updates the Master Profile personal information blob.
    """
    try:
        await ProfileManager.update_personal_info(session, current_user.id, info)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "message": "Personal info updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update personal info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error updating personal info")

@router.post("/educations", status_code=status.HTTP_201_CREATED)
async def upsert_education(
    edu_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Adds or updates a school record in education timeline.
    """
    try:
        edu = await ProfileManager.upsert_education(session, current_user.id, edu_data)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "id": str(edu.id)}
    except Exception as e:
        logger.error(f"Failed to upsert education: {e}")
        raise HTTPException(status_code=500, detail="Internal server error updating education record")

@router.delete("/educations/{id}", status_code=status.HTTP_200_OK)
async def delete_education(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Deletes an education record.
    """
    try:
        await ProfileManager.delete_education(session, current_user.id, id)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "message": "Education deleted"}
    except Exception as e:
        logger.error(f"Failed to delete education: {e}")
        raise HTTPException(status_code=500, detail="Internal server error deleting education record")

@router.post("/experiences", status_code=status.HTTP_201_CREATED)
async def upsert_experience(
    exp_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Adds or updates an employment history record.
    """
    try:
        exp = await ProfileManager.upsert_experience(session, current_user.id, exp_data)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "id": str(exp.id)}
    except Exception as e:
        logger.error(f"Failed to upsert experience: {e}")
        raise HTTPException(status_code=500, detail="Internal server error updating experience record")

@router.delete("/experiences/{id}", status_code=status.HTTP_200_OK)
async def delete_experience(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Deletes an experience record.
    """
    try:
        await ProfileManager.delete_experience(session, current_user.id, id)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "message": "Experience deleted"}
    except Exception as e:
        logger.error(f"Failed to delete experience: {e}")
        raise HTTPException(status_code=500, detail="Internal server error deleting experience record")

@router.post("/projects", status_code=status.HTTP_201_CREATED)
async def upsert_project(
    proj_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Adds or updates a portfolio project record.
    """
    try:
        proj = await ProfileManager.upsert_project(session, current_user.id, proj_data)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "id": str(proj.id)}
    except Exception as e:
        logger.error(f"Failed to upsert project: {e}")
        raise HTTPException(status_code=500, detail="Internal server error updating project record")

@router.delete("/projects/{id}", status_code=status.HTTP_200_OK)
async def delete_project(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Deletes a project record.
    """
    try:
        await ProfileManager.delete_project(session, current_user.id, id)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "message": "Project deleted"}
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        raise HTTPException(status_code=500, detail="Internal server error deleting project record")

@router.post("/certifications", status_code=status.HTTP_201_CREATED)
async def upsert_certification(
    cert_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Adds or updates a professional certification record.
    """
    try:
        cert = await ProfileManager.upsert_certification(session, current_user.id, cert_data)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "id": str(cert.id)}
    except Exception as e:
        logger.error(f"Failed to upsert certification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error updating certification record")

@router.delete("/certifications/{id}", status_code=status.HTTP_200_OK)
async def delete_certification(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Deletes a certification record.
    """
    try:
        await ProfileManager.delete_certification(session, current_user.id, id)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "message": "Certification deleted"}
    except Exception as e:
        logger.error(f"Failed to delete certification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error deleting certification record")

@router.post("/skills", status_code=status.HTTP_201_CREATED)
async def add_skill(
    skill_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Adds or updates a user skill fact.
    AI inferred information is not auto-verified.
    """
    try:
        skill = await ProfileManager.add_user_skill(
            session=session,
            user_id=current_user.id,
            name=skill_data["name"],
            category=skill_data.get("category", "general"),
            proficiency=skill_data.get("proficiency", "Intermediate"),
            status=skill_data.get("status", "USER_PROVIDED"),
            evidence_ids=skill_data.get("evidence", [])
        )
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "id": str(skill.id), "verification_status": skill.status}
    except Exception as e:
        logger.error(f"Failed to add skill: {e}")
        raise HTTPException(status_code=500, detail="Internal server error adding skill")

@router.patch("/skills/{id}", status_code=status.HTTP_200_OK)
async def update_skill_status(
    id: uuid.UUID,
    skill_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Promotes or modifies a skill status (e.g. USER REVIEW -> USER APPROVES / VERIFIED).
    """
    try:
        status_val = skill_data.get("status")
        if not status_val:
            raise HTTPException(status_code=400, detail="Missing status parameter")
            
        skill = await ProfileManager.update_user_skill_status(session, current_user.id, id, status_val)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "message": "Skill status updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update skill status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error updating skill status")

@router.delete("/skills/{id}", status_code=status.HTTP_200_OK)
async def delete_skill(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Deletes a skill record.
    """
    try:
        await ProfileManager.delete_skill(session, current_user.id, id)
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "message": "Skill deleted"}
    except Exception as e:
        logger.error(f"Failed to delete skill: {e}")
        raise HTTPException(status_code=500, detail="Internal server error deleting skill")

@router.post("/evidence", status_code=status.HTTP_201_CREATED)
async def add_evidence(
    ev_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Ingests a new canonical evidence registry fact.
    """
    try:
        evidence = await ProfileManager.add_evidence(
            session=session,
            user_id=current_user.id,
            evidence_type=ev_data["type"],
            description=ev_data["description"],
            source_url=ev_data.get("source_url"),
            properties=ev_data.get("properties")
        )
        await ProfileManager.sync_graph_projection(session, current_user.id)
        return {"status": "success", "id": str(evidence.id)}
    except Exception as e:
        logger.error(f"Failed to add evidence: {e}")
        raise HTTPException(status_code=500, detail="Internal server error adding evidence")

@router.put("/goals", status_code=status.HTTP_200_OK)
async def update_goals(
    goals_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Updates the career target goals and application preferences.
    """
    try:
        await ProfileManager.update_goals(session, current_user.id, goals_data)
        return {"status": "success", "message": "Goals updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update career goals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error updating career goals")

@router.get("/skills", status_code=status.HTTP_200_OK)
async def get_skills(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    """
    GET /api/v1/career/skills
    Retrieves the current user's skills inventory.
    """
    from sqlalchemy import select
    from app.models.master_profile import UserSkill
    result = await session.execute(
        select(UserSkill)
        .filter(UserSkill.user_id == current_user.id)
        .order_by(UserSkill.name.asc())
    )
    skills = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "category": s.category,
            "proficiency_level": s.proficiency_level,
            "status": s.status,
            "evidence": s.evidence
        } for s in skills
    ]

@router.get("/evidence", status_code=status.HTTP_200_OK)
async def get_evidence(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    """
    GET /api/v1/career/evidence
    Retrieves the current user's evidence registry logs.
    """
    from sqlalchemy import select
    from app.models.master_profile import Evidence
    result = await session.execute(
        select(Evidence)
        .filter(Evidence.user_id == current_user.id)
        .order_by(Evidence.created_at.desc())
    )
    evs = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "evidence_type": e.evidence_type,
            "description": e.description,
            "verification_source": e.verification_source,
            "verification_status": e.verification_status,
            "created_at": e.created_at.isoformat()
        } for e in evs
    ]

@router.get("/goals", status_code=status.HTTP_200_OK)
async def get_goals(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    """
    GET /api/v1/career/goals
    Retrieves the current user's active career goals list.
    """
    from sqlalchemy import select
    from app.models.master_profile import CareerGoal
    result = await session.execute(
        select(CareerGoal)
        .filter(CareerGoal.user_id == current_user.id)
        .order_by(CareerGoal.created_at.desc())
    )
    goals = result.scalars().all()
    return [
        {
            "id": str(g.id),
            "title": g.title,
            "goal_type": g.goal_type,
            "target_date": g.target_date,
            "status": g.status
        } for g in goals
    ]
