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
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Dependency resolving the active user object.
    Bypasses JWT auth in local development and returns a default mock user.
    """
    import uuid
    mock_id = "00000000-0000-0000-0000-000000000000"
    logger.info(f"UAT Mode: resolving default mock user ID: {mock_id}")
    user = await user_repo.get_by_id(mock_id)
    if not user:
        user = User(
            id=uuid.UUID(mock_id),
            email="mockuser@careeros.local",
            full_name="Mock Developer",
            hashed_password="mock_password",
            role=UserRole.MEMBER,
            is_active=True
        )
        user_repo.session.add(user)
        await user_repo.session.flush()
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
