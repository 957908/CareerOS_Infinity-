import logging
import datetime
from typing import Optional
import jwt
from jwt import PyJWTError

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

logger = logging.getLogger("app.core.security")

# Crypt context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare raw input password against stored hash.
    """
    logger.info("Verifying password comparison.")
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate secure salted hash for store password.
    """
    logger.info("Generating password hash.")
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Generates signed JWT access token for authentication sessions.
    """
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"JWT access token generated successfully for subject: {subject}")
    return encoded_jwt

async def verify_token_subject(token: str = Depends(oauth2_scheme)) -> str:
    """
    FastAPI dependency validating authentication token signatures.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject: Optional[str] = payload.get("sub")
        if subject is None:
            logger.warning("JWT payload contains no subject claim.")
            raise credentials_exception
        return subject
    except PyJWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise credentials_exception

