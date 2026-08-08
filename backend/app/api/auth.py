import logging
from typing import Optional
from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.core.database import get_db_session
from app.services.auth_service import AuthService

logger = logging.getLogger("app.api.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Registers a new user, hashes their credentials, and logs the registration.
    """
    logger.info(f"API Register: user registration request: {payload.email}")
    user = await AuthService.register_user(
        session=session,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name
    )
    await AuthService.write_audit_log(
        session=session,
        action="USER_REGISTRATION",
        user_id=user.id,
        details=f"Email: {user.email}"
    )
    return {"user_id": str(user.id), "email": user.email, "message": "User registered successfully."}

@router.post("/token", status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Validates user credentials, issues JWT access token, and sets secure refresh token cookie.
    """
    logger.info(f"API Login: user token request: {payload.email}")
    user, access_token = await AuthService.authenticate_user(
        session=session,
        email=payload.email,
        password=payload.password
    )
    
    # Create and write refresh token
    refresh_token = await AuthService.create_session_refresh_token(
        session=session,
        user_id=user.id
    )
    
    # Set HttpOnly cookie for session security
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=30 * 86400  # 30 days
    )
    
    await AuthService.write_audit_log(
        session=session,
        action="USER_LOGIN_SUCCESS",
        user_id=user.id,
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600
    }

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Validates refresh token cookie and issues new access token.
    """
    logger.info("API Refresh: session token refresh request.")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning("Session refresh failed: missing refresh_token cookie.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session refresh token is missing."
        )
        
    access_token = await AuthService.refresh_access_session(
        session=session,
        token_str=refresh_token
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Revokes the active user session and clears authentication cookies.
    """
    logger.info("API Logout: logging user session out.")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully."}
