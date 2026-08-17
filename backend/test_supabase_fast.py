import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.domain import Base
from app.services.sync_service import KommoSyncService
from app.core.database import async_sessionmaker, AsyncSession
from app.core.config import settings

async def run():
    print("Testing database connection using configured DATABASE_URL from settings...")
    db_url = settings.DATABASE_URL
    connect_args = {"statement_cache_size": 0} if "asyncpg" in db_url else {}
    engine = create_async_engine(db_url, connect_args=connect_args, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("SUCCESS: Database schema initialized!")

    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        sync_service = KommoSyncService(session)
        res = await sync_service.execute_sync(trigger_type="manual")
        print("SUCCESS: Sync executed:", res)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run())
