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
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'Consultora';
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

        # 4. Patch domain tables if they exist
        await conn.execute(text("""
            DO $$
            BEGIN
                -- COMPANIES
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'companies') THEN
                    ALTER TABLE companies ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE companies ADD COLUMN IF NOT EXISTS external_id INTEGER;
                    ALTER TABLE companies ADD COLUMN IF NOT EXISTS custom_fields_values JSONB;
                END IF;

                -- CONTACTS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'contacts') THEN
                    ALTER TABLE contacts ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE contacts ADD COLUMN IF NOT EXISTS external_id INTEGER;
                    ALTER TABLE contacts ADD COLUMN IF NOT EXISTS custom_fields_values JSONB;
                END IF;

                -- PIPELINES
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'pipelines') THEN
                    ALTER TABLE pipelines ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE pipelines ADD COLUMN IF NOT EXISTS external_id INTEGER;
                    ALTER TABLE pipelines ADD COLUMN IF NOT EXISTS is_main BOOLEAN DEFAULT false;
                    ALTER TABLE pipelines ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;
                END IF;

                -- LEAD_STATUS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'lead_status') THEN
                    ALTER TABLE lead_status ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE lead_status ADD COLUMN IF NOT EXISTS external_id INTEGER;
                    ALTER TABLE lead_status ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;
                    ALTER TABLE lead_status ADD COLUMN IF NOT EXISTS color VARCHAR(50);
                    ALTER TABLE lead_status ADD COLUMN IF NOT EXISTS type INTEGER DEFAULT 1;
                END IF;

                -- TAGS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tags') THEN
                    ALTER TABLE tags ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE tags ADD COLUMN IF NOT EXISTS external_id INTEGER;
                    ALTER TABLE tags ADD COLUMN IF NOT EXISTS color VARCHAR(50);
                END IF;

                -- CUSTOM_FIELDS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'custom_fields') THEN
                    ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS external_id INTEGER;
                    ALTER TABLE custom_fields ADD COLUMN IF NOT EXISTS code VARCHAR(100);
                END IF;

                -- LEADS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'leads') THEN
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS external_id INTEGER;
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS closed_at TIMESTAMP WITH TIME ZONE;
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS unidade VARCHAR(100);
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS procedimento VARCHAR(100);
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS origem VARCHAR(100);
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS suborigem VARCHAR(100);
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS loss_reason VARCHAR(255);
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS first_response_time_minutes FLOAT;
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS sales_cycle_days FLOAT;
                    ALTER TABLE leads ADD COLUMN IF NOT EXISTS custom_fields_values JSONB;
                END IF;

                -- TASKS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks') THEN
                    ALTER TABLE tasks ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE tasks ADD COLUMN IF NOT EXISTS external_id INTEGER;
                    ALTER TABLE tasks ADD COLUMN IF NOT EXISTS resolution_time_hours FLOAT;
                END IF;

                -- EVENTS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'events') THEN
                    ALTER TABLE events ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                    ALTER TABLE events ADD COLUMN IF NOT EXISTS external_id VARCHAR(100);
                END IF;

                -- LEAD_HISTORY
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'lead_history') THEN
                    ALTER TABLE lead_history ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                END IF;

                -- SYNC_LOGS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sync_logs') THEN
                    ALTER TABLE sync_logs ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                END IF;

                -- CRM_INTEGRATIONS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'crm_integrations') THEN
                    ALTER TABLE crm_integrations ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
                END IF;

                -- INTEGRATION_LOGS
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'integration_logs') THEN
                    ALTER TABLE integration_logs ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE;
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

