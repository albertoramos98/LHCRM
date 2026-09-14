import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine. Supports both PostgreSQL (asyncpg) and SQLite (aiosqlite)
connect_args = {"statement_cache_size": 0} if "asyncpg" in settings.DATABASE_URL else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def _safe_postgres_migration(conn):
    """
    Safely ensures multi-tenant columns and tables exist in PostgreSQL
    if tables already existed prior to the multi-tenant upgrade.
    """
    try:
        # 1. Ensure organizations exists
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS organizations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # 2. Patch users table if it exists
        await conn.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL;
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS external_id INTEGER;
                END IF;
            END $$;
        """))

        # 3. Ensure organization_members exists
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS organization_members (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(50) NOT NULL DEFAULT 'Consultora',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_org_member_org_user UNIQUE (organization_id, user_id)
            );
        """))

        # 4. Patch domain tables if they exist without organization_id
        for table_name in [
            "companies", "contacts", "pipelines", "lead_status", "tags",
            "custom_fields", "leads", "tasks", "events", "lead_history",
            "sync_logs", "crm_integrations", "integration_logs"
        ]:
            await conn.execute(text(f"""
                DO $$
                BEGIN
                    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}') THEN
                        BEGIN
                            ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                        EXCEPTION WHEN OTHERS THEN
                            NULL;
                        END;
                    END IF;
                END $$;
            """))
    except Exception as exc:
        logger.warning(f"Self-healing Postgres schema update notice: {exc}")

async def init_db():
    async with engine.begin() as conn:
        # 1. Safe patch for PostgreSQL legacy schemas
        if "postgresql" in settings.DATABASE_URL or "asyncpg" in settings.DATABASE_URL:
            await _safe_postgres_migration(conn)
        
        # 2. Create any missing tables
        await conn.run_sync(Base.metadata.create_all)

