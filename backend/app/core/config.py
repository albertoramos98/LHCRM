import os
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "LHCRM - Dashboard Executivo"
    ENVIRONMENT: str = "development"
    
    SECRET_KEY: str = "insecure-dev-secret-key-please-set-in-env-file-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Default to local SQLite for development; production MUST set DATABASE_URL in .env
    DATABASE_URL: str = "sqlite+aiosqlite:///./lhcrm.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: Optional[str]) -> str:
        if not v:
            return "sqlite+aiosqlite:///./lhcrm.db"
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None

    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000"
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            v_trimmed = v.strip()
            if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
                try:
                    return json.loads(v_trimmed)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    KOMMO_SUBDOMAIN: Optional[str] = "demo"
    KOMMO_CLIENT_ID: Optional[str] = None
    KOMMO_CLIENT_SECRET: Optional[str] = None
    KOMMO_REDIRECT_URI: Optional[str] = "http://localhost:8000/api/integrations/kommo/callback"
    KOMMO_LONG_LIVED_TOKEN: Optional[str] = None

    CACHE_TTL_SECONDS: int = 60
    AUTO_SYNC_INTERVAL_MINUTES: int = 5
    
    # Rate Limiting
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 10
    RATE_LIMIT_SYNC_PER_MINUTE: int = 5

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

