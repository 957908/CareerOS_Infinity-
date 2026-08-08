import logging
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.security import verify_token_subject
from app.core.exceptions import AuthenticationError, PermissionDenied
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole

logger = logging.getLogger("app.core.dependencies")

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """
    Dependency returning an active instance of the UserRepository class.
    """
    return UserRepository(session)

async def get_current_user(
    subject: str = Depends(verify_token_subject),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Dependency resolving the active user object from the authentication token.
    """
    logger.info(f"Resolving active user object for subject: {subject}")
    user = await user_repo.get_by_id(subject)
    if not user or not user.is_active or user.is_deleted:
        logger.warning(f"User validation failed for user ID: {subject}")
        raise AuthenticationError("User is inactive or has been deleted.")
    return user

class RoleChecker:
    """
    Role verification dependency checking if the user holds required access permissions.
    """
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        logger.info(f"RoleChecker: checking user role: {current_user.role} against allowed: {self.allowed_roles}")
        if current_user.role not in self.allowed_roles:
            logger.warning(f"User ID: {current_user.id} role: {current_user.role} denied access.")
            raise PermissionDenied("Insufficient permissions to access this resource.")
        return current_user
