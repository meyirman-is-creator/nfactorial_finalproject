import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    # Security
    ADMIN_EMAIL: EmailStr = "admin@example.com"
    ADMIN_PASSWORD: str = "adminpassword"

    # AI Integration
    OPENAI_API_KEY: Optional[str] = None

    # Project info
    PROJECT_NAME: str = "LMS Platform"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()