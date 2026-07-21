from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "LHCRM - Dashboard Executivo"
    SECRET_KEY: str = "super-secret-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "postgresql+asyncpg://postgres:010898dejaneiro!@db.evkligtiojtsxtqydtog.supabase.co:5432/postgres"

    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None

    FRONTEND_URL: str = "http://localhost:3000"

    KOMMO_SUBDOMAIN: Optional[str] = "demo"
    KOMMO_CLIENT_ID: Optional[str] = "demo_client_id"
    KOMMO_CLIENT_SECRET: Optional[str] = "demo_client_secret"
    KOMMO_REDIRECT_URI: Optional[str] = "http://localhost:8000/api/integrations/kommo/callback"
    KOMMO_LONG_LIVED_TOKEN: Optional[str] = "demo_token"

    CACHE_TTL_SECONDS: int = 60
    AUTO_SYNC_INTERVAL_MINUTES: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
