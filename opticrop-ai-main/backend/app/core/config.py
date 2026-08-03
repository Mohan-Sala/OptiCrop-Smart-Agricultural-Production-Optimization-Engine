import os
from typing import Any, Dict, List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App General Settings
    APP_NAME: str = "OptiCrop AI Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # API Version Prefix
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "temp-fallback-secret-key-ensure-replaced-in-env"
    JWT_SECRET: str = "temp-fallback-jwt-secret-key-ensure-replaced-in-env"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # Supabase & PostgreSQL Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    STORAGE_BUCKET: Optional[str] = None

    # CORS Configurations
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return []

    # File System Configurations
    UPLOAD_PATH: str = "tmp/uploads"
    MODEL_PATH: str = "models"

    # Centralized Logging
    LOG_LEVEL: str = "INFO"

    # Settings configurations to support loading from .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
