import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import BaseRepository
from app.models.resume import Resume

logger = logging.getLogger("app.repositories.resume_repository")

class ResumeRepository(BaseRepository[Resume]):
    """
    Resume repository executing relational query operations for parsed resumes.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Resume, session)

    async def get_resumes_by_user_id(self, user_id: str) -> List[Resume]:
        logger.info(f"ResumeRepository: querying resumes list for user ID: {user_id}")
        query = select(Resume).filter(Resume.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save_new_resume(
        self,
        user_id: str,
        file_url: str,
        raw_text: str,
        resume_json: dict,
        embedding: list
    ) -> Resume:
        logger.info(f"ResumeRepository: saving new parsed resume instance for user ID: {user_id}")
        resume = Resume(
            user_id=user_id,
            file_url=file_url,
            raw_text=raw_text,
            resume_json=resume_json,
            embedding=embedding
        )
        self.session.add(resume)
        await self.session.flush()
        return resume
