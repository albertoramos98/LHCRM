import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.domain import Base
from app.services.sync_service import KommoSyncService
from app.core.database import async_sessionmaker, AsyncSession

DB_URL = "postgresql+asyncpg://postgres:010898dejaneiro!@db.evkligtiojtsxtqydtog.supabase.co:5432/postgres"

async def run():
    print("Testing Supabase Session Pooler (port 5432) with statement_cache_size=0...")
    engine = create_async_engine(DB_URL, connect_args={"statement_cache_size": 0}, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("SUCCESS: Tables created in Supabase!")

    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        sync_service = KommoSyncService(session)
        res = await sync_service.execute_sync(trigger_type="manual")
        print("SUCCESS: Sync executed:", res)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run())
