import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.sync_service import KommoSyncService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_kommo_sync_job():
    logger.info("Executing 5-minute scheduled Kommo CRM auto-sync job...")
    async with AsyncSessionLocal() as session:
        sync_service = KommoSyncService(session)
        result = await sync_service.execute_sync(trigger_type="automatic")
        logger.info(f"Auto-sync job finished with result: {result['status']}")

def start_scheduler():
    interval_minutes = settings.AUTO_SYNC_INTERVAL_MINUTES
    scheduler.add_job(
        scheduled_kommo_sync_job,
        "interval",
        minutes=interval_minutes,
        id="kommo_auto_sync_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"APScheduler started: Kommo CRM auto-sync running every {interval_minutes} minutes.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down.")
