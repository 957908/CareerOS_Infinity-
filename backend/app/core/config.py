import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Configure basic application logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.core.config")

class Settings(BaseSettings):
    """
    CareerOS Infinity Core Settings Configuration.
    Loads configurations from environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = Field(default="CareerOS Infinity")
    VERSION: str = Field(default="1.0.0")
    API_V1_STR: str = Field(default="/api/v1")

    # DB Configurations
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:secure_postgres_password@db:5432/careeros_db"
    )

    # Redis Cache / Broker configs
    REDIS_URL: str = Field(
        default="redis://redis:6379/0"
    )

    # AI Configurations
    GEMINI_API_KEY: str = Field(default="")

    # Email Sync Configurations (Optional Real Inbox Connection)
    IMAP_USER_EMAIL: str = Field(default="")
    GMAIL_APP_PASSWORD: str = Field(default="")

    # Security Keys
    SECRET_KEY: str = Field(
        default="super_secret_jwt_sign_key_rotating_32_bytes_len"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)

# Instantiate single settings instance
settings = Settings()

import os
if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY

logger.info("Application settings loaded successfully.")

