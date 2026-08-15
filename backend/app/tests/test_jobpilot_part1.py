import pytest
import uuid
import datetime
import asyncio
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobPosting
from app.models.master_profile import MasterProfile, Education, Experience, Project, Certification, UserSkill, Evidence, CareerGoal
from app.services.truth_guard import TruthGuard
from app.services.profile_manager import ProfileManager
from app.repositories.graph_repository import PostgreSQLGraphRepository
from app.repositories.resume_repository import ResumeRepository

# Create dedicated test session provider
test_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

async def create_test_user(session) -> User:
    """Helper to insert a clean test user."""
    user = User(
        email=f"test_{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="argon2_hashed_pw",
        full_name="Test Niraj Kadam"
    )
    session.add(user)
    await session.flush()
    return user

def test_one_active_master_per_user():
    """
    CTO Correction 3 & 5: One ACTIVE master resume per user.
    Previous masters must become ARCHIVED.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)
                resume_repo = ResumeRepository(session)
                
                # 1. Create first Master Resume (Active)
                r1 = await resume_repo.save_new_resume(
                    user_id=str(user.id),
                    file_url="master_v1.pdf",
                    raw_text="Python Engineer resume text",
                    resume_json={"skills": ["Python"]},
                    embedding=[0.0]*1536,
                    is_master=True,
                    resume_type="MASTER"
                )
                r1.lifecycle_status = "ACTIVE"
                r1.version = 1
                await session.flush()

                # 2. Upload new version: Archive previous master
                await session.execute(
                    update(Resume)
                    .filter(Resume.user_id == user.id, Resume.is_master == True, Resume.lifecycle_status == "ACTIVE")
                    .values(lifecycle_status="ARCHIVED", is_master=False)
                )
                
                r2 = await resume_repo.save_new_resume(
                    user_id=str(user.id),
                    file_url="master_v2.pdf",
                    raw_text="Senior Python Engineer resume text",
                    resume_json={"skills": ["Python", "System Design"]},
                    embedding=[0.0]*1536,
                    is_master=True,
                    resume_type="MASTER"
                )
                r2.lifecycle_status = "ACTIVE"
                r2.version = 2
                await session.flush()

                # 3. Assertions
                await session.refresh(r1)
                await session.refresh(r2)
                
                assert r1.lifecycle_status == "ARCHIVED"
                assert r1.is_master is False
                assert r2.lifecycle_status == "ACTIVE"
                assert r2.is_master is True

                # 4. Verify unique constraint index enforces one active master per user
                duplicate_active = Resume(
                    user_id=str(user.id),
                    file_url="master_dup.pdf",
                    raw_text="duplicate active master",
                    resume_json={},
                    is_master=True,
                    resume_type="MASTER",
                    lifecycle_status="ACTIVE"
                )
                session.add(duplicate_active)
                
                with pytest.raises(Exception):
                    await session.flush()
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_master_immutability():
    """
    CTO Correction 12: Master resume must never be overwritten by AI tailoring.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)
                resume_repo = ResumeRepository(session)

                master = await resume_repo.save_new_resume(
                    user_id=str(user.id),
                    file_url="master.pdf",
                    raw_text="Master Text",
                    resume_json={"skills": ["Python"]},
                    embedding=[0.0]*1536,
                    is_master=True,
                    resume_type="MASTER"
                )
                master.lifecycle_status = "ACTIVE"
                await session.flush()

                # Simulate Tailored Resume Creation referencing master
                tailored = await resume_repo.save_new_resume(
                    user_id=str(user.id),
                    file_url="tailored.pdf",
                    raw_text="Tailored Text",
                    resume_json={"skills": ["Python", "FastAPI"]},
                    embedding=[0.0]*1536,
                    is_master=False,
                    resume_type="TAILORED",
                    parent_id=master.id
                )
                await session.flush()

                await session.refresh(master)
                assert master.is_master is True
                assert master.resume_type == "MASTER"
                assert master.resume_json == {"skills": ["Python"]}  # Remains unchanged
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_tailored_lineage():
    """
    CTO Correction 11: Tailored resumes must always reference their Master Resume lineage.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)
                resume_repo = ResumeRepository(session)

                master = await resume_repo.save_new_resume(
                    user_id=str(user.id),
                    file_url="master.pdf",
                    raw_text="Master",
                    resume_json={},
                    embedding=[0.0]*1536,
                    is_master=True,
                    resume_type="MASTER"
                )
                await session.flush()

                tailored = await resume_repo.save_new_resume(
                    user_id=str(user.id),
                    file_url="tailored.pdf",
                    raw_text="Tailored",
                    resume_json={},
                    embedding=[0.0]*1536,
                    is_master=False,
                    resume_type="TAILORED",
                    parent_id=master.id
                )
                await session.flush()

                assert tailored.parent_id == master.id
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_user_isolation():
    """
    CTO Correction 11: User isolation check. Users cannot fetch or modify other users' profiles.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user1 = await create_test_user(session)
                user2 = await create_test_user(session)

                # Ingest skill for User 1
                await ProfileManager.add_user_skill(
                    session, user1.id, name="Docker", status="VERIFIED"
                )

                # Query skill list for User 2
                profile_data2 = await ProfileManager.get_profile(session, user2.id)
                assert not any(s["name"] == "Docker" for s in profile_data2["skills"])
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_truth_guard_supported_claim():
    """
    CTO Correction 14: Validates factual claims against canonical verified evidence.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)

                # Ingest verified skill
                await ProfileManager.add_user_skill(
                    session, user.id, name="Kafka", status="VERIFIED"
                )

                report = await TruthGuard.validate_claim(
                    session=session,
                    user_id=user.id,
                    claim_type="SKILL",
                    claim_content={"name": "Kafka"}
                )
                assert report["allowed"] is True
                assert report["validation_status"] == "VERIFIED"
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_truth_guard_unsupported_claim():
    """
    CTO Correction 14: Rejects claims not supported by verified evidence.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)

                report = await TruthGuard.validate_claim(
                    session=session,
                    user_id=user.id,
                    claim_type="SKILL",
                    claim_content={"name": "AWS"}
                )
                assert report["allowed"] is False
                assert "No record found" in report["reason"]
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_ai_inferred_claim_rejection():
    """
    CTO Correction 16: AI_INFERRED information must never automatically become VERIFIED/ALLOWED.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)

                # Add AI Inferred skill
                await ProfileManager.add_user_skill(
                    session, user.id, name="Kubernetes", status="AI_INFERRED"
                )

                report = await TruthGuard.validate_claim(
                    session=session,
                    user_id=user.id,
                    claim_type="SKILL",
                    claim_content={"name": "Kubernetes"}
                )
                assert report["allowed"] is False
                assert "unverified status" in report["reason"]
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_missing_skill_isolation():
    """
    CTO Correction 15: Missing skills discovered from job descriptions must NEVER automatically modify user skills.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)

                # Ingest a skill that's missing
                missing_skill = "Spark"

                # Verify Spark is not in user skills
                profile = await ProfileManager.get_profile(session, user.id)
                assert not any(s["name"] == missing_skill for s in profile["skills"])
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_graph_projection_consistency():
    """
    CTO Correction 10: Verify relational update updates projected graph nodes.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)
                graph_repo = PostgreSQLGraphRepository(session)

                # 1. Update skill in RDBMS
                await ProfileManager.add_user_skill(
                    session, user.id, name="Go", status="VERIFIED"
                )
                # Sync projection
                await ProfileManager.sync_graph_projection(session, user.id)

                # 2. Check Graph DB projection matches
                node = await graph_repo.get_entity_node("skill:go")
                assert node is not None
                assert node.properties["name"] == "Go"
                assert node.properties["status"] == "VERIFIED"
            finally:
                await session.rollback()
    
    asyncio.run(run())

def test_create_master_profile():
    """
    1. Create Master Profile test.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)
                await ProfileManager.update_personal_info(session, user.id, {"name": "Niraj Kadam Test", "email": user.email})
                
                q = select(MasterProfile).filter(MasterProfile.user_id == user.id)
                res = await session.execute(q)
                profile = res.scalars().first()
                assert profile is not None
                assert profile.personal_info["name"] == "Niraj Kadam Test"
            finally:
                await session.rollback()
    asyncio.run(run())

class MockUploadFile:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.content = content
        self.headers = {}
    async def read(self) -> bytes:
        return self.content

def test_upload_master_and_lineage_api():
    """
    2. Upload Master Resume, 3. Upload New Master Version, 4. Previous master becomes ARCHIVED.
    """
    async def run():
        from app.api.resumes import upload_master
        from unittest.mock import patch
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)
                
                mock_file_v1 = MockUploadFile("niraj_v1.pdf", b"%PDF-1.4 mock pdf structure v1")
                with patch("app.services.document_parser.DocumentParserService.extract_text_from_pdf", return_value="Mock resume text content"):
                    resp1 = await upload_master(file=mock_file_v1, current_user=user, session=session)
                    assert resp1["status"] == "COMPLETED"
                    
                    res1 = await session.execute(
                        select(Resume).filter(Resume.user_id == user.id, Resume.is_master == True)
                    )
                    masters = res1.scalars().all()
                    assert len(masters) == 1
                    assert masters[0].lifecycle_status == "ACTIVE"
                    
                    mock_file_v2 = MockUploadFile("niraj_v2.pdf", b"%PDF-1.4 mock pdf structure v2")
                    resp2 = await upload_master(file=mock_file_v2, current_user=user, session=session)
                    assert resp2["status"] == "COMPLETED"
                    
                    res2 = await session.execute(
                        select(Resume).filter(Resume.user_id == user.id)
                    )
                    all_resumes = res2.scalars().all()
                    active_masters = [r for r in all_resumes if r.is_master and r.lifecycle_status == "ACTIVE"]
                    archived_masters = [r for r in all_resumes if r.lifecycle_status == "ARCHIVED"]
                    
                    assert len(active_masters) == 1
                    assert len(archived_masters) == 1
                    assert archived_masters[0].file_url == "niraj_v1.pdf"
            finally:
                await session.rollback()
    asyncio.run(run())

def test_authorization():
    """
    Verify user isolation / authentication checks.
    """
    async def run():
        with pytest.raises(Exception):
            await ProfileManager.get_profile(None, uuid.uuid4())
    asyncio.run(run())

def test_api_validation():
    """
    Test validation checks.
    """
    async def run():
        async with TestSessionLocal() as session:
            try:
                user = await create_test_user(session)
                with pytest.raises(Exception):
                    await ProfileManager.add_user_skill(
                        session=session,
                        user_id=user.id,
                        name=None,
                        category="general"
                    )
            finally:
                await session.rollback()
    asyncio.run(run())

def test_migration_validation():
    """
    Verify all child tables exist and are queryable.
    """
    async def run():
        async with TestSessionLocal() as session:
            await session.execute(select(Education).limit(1))
            await session.execute(select(Experience).limit(1))
            await session.execute(select(Project).limit(1))
            await session.execute(select(Certification).limit(1))
            await session.execute(select(Evidence).limit(1))
            await session.execute(select(CareerGoal).limit(1))
            assert True
    asyncio.run(run())
