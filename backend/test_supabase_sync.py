import asyncio
import logging
from app.core.database import init_db, AsyncSessionLocal
from app.services.sync_service import KommoSyncService

logging.basicConfig(level=logging.INFO)

async def main():
    print("Connecting to Supabase PostgreSQL database and creating tables...")
    await init_db()
    print("Database tables created successfully in Supabase!")

    async with AsyncSessionLocal() as session:
        sync_service = KommoSyncService(session)
        result = await sync_service.execute_sync(trigger_type="manual")
        print("Initial Sync Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
