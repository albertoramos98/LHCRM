from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

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

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
