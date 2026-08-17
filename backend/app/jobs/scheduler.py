import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.domain import Organization
from app.integrations.kommo.models import CRMIntegration
from app.integrations.kommo.sync import KommoIntegrationSyncService
from app.services.sync_service import KommoSyncService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_kommo_sync_job():
    logger.info("Executing scheduled Kommo CRM auto-sync job for active tenant organizations...")
    async with AsyncSessionLocal() as session:
        # 1. Fetch all active organizations
        orgs_res = await session.execute(select(Organization).where(Organization.is_active == True))
        active_orgs = list(orgs_res.scalars().all())

        if not active_orgs:
            logger.info("No active organizations found for auto-sync.")
            return

        for org in active_orgs:
            try:
                # Check for active connected Kommo integration for this organization
                int_res = await session.execute(
                    select(CRMIntegration).where(
                        CRMIntegration.organization_id == org.id,
                        CRMIntegration.status == "connected"
                    )
                )
                integration = int_res.scalar_one_or_none()

                if integration:
                    logger.info(f"Auto-syncing Kommo CRM for Org '{org.name}' (ID: {org.id}, Subdomain: {integration.subdomain})...")
                    sync_service = KommoIntegrationSyncService(session, organization_id=org.id)
                    await sync_service.sync_integration(integration.id, trigger_type="automatic")
                else:
                    # Execute local/demo sync if configured for organization
                    sync_service = KommoSyncService(session, organization_id=org.id)
                    latest_log = await sync_service.get_latest_sync_status()
                    if latest_log["status"] == "never_run":
                        logger.info(f"Executing initial sync for Org '{org.name}' (ID: {org.id})...")
                        await sync_service.execute_sync(trigger_type="automatic")

                # Generate updated HTML dashboard for tenant
                try:
                    from app.services.html_generator import generate_dashboard_html
                    await generate_dashboard_html(
                        session,
                        organization_id=org.id,
                        output_path=f"static/dashboard_{org.slug}.html"
                    )
                except Exception as e:
                    logger.error(f"Failed to generate HTML dashboard for Org {org.id}: {e}")

            except Exception as e:
                logger.error(f"Error during auto-sync for Org '{org.name}' (ID: {org.id}): {e}", exc_info=True)

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
