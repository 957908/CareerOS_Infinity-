import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import BaseRepository
from app.models.user import User

logger = logging.getLogger("app.repositories.user_repository")

class UserRepository(BaseRepository[User]):
    """
    User repository implementing optimized relational query methods and soft delete mappings.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve active, non-deleted user matching specified email address.
        """
        logger.info(f"UserRepository: querying user by email: {email}")
        query = select(User).filter(
            User.email == email,
            User.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def soft_delete_user(self, user: User) -> None:
        """
        Sets is_deleted tag to True, preventing typical logins but keeping historical records intact.
        """
        logger.info(f"UserRepository: performing soft delete for user ID: {user.id}")
        user.is_deleted = True
        self.session.add(user)
        await self.session.flush()
