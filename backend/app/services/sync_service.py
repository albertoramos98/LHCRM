import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.base import CRMProvider
from app.providers.kommo_provider import KommoProvider
from app.repositories.sync_repository import SyncRepository
from app.core.cache import memory_cache

logger = logging.getLogger(__name__)

class KommoSyncService:
    """
    Service responsible for synchronizing Kommo CRM entities into local PostgreSQL.
    Supports manual & automatic triggers, logs sync progress, and clears API cache upon sync completion.
    """

    def __init__(self, session: AsyncSession, provider: CRMProvider = None):
        self.session = session
        self.provider = provider or KommoProvider()
        self.repository = SyncRepository(session)

    async def execute_sync(self, trigger_type: str = "automatic") -> dict:
        log = await self.repository.create_sync_log(trigger_type=trigger_type)
        logger.info(f"Starting CRM synchronization (Log ID #{log.id}, trigger: {trigger_type})...")

        items_count = 0
        try:
            # 1. Fetch & Upsert Users
            users = await self.provider.get_users()
            items_count += await self.repository.upsert_users(users)

            # 2. Fetch & Upsert Pipelines & Statuses
            pipelines = await self.provider.get_pipelines()
            items_count += await self.repository.upsert_pipelines_and_statuses(pipelines)

            # 3. Fetch & Upsert Custom Fields & Tags
            custom_fields = await self.provider.get_custom_fields()
            items_count += await self.repository.upsert_custom_fields(custom_fields)

            tags = await self.provider.get_tags()
            items_count += await self.repository.upsert_tags(tags)

            # 4. Fetch & Upsert Contacts & Companies
            contacts = await self.provider.get_contacts()
            items_count += await self.repository.upsert_contacts(contacts)

            companies = await self.provider.get_companies()
            items_count += await self.repository.upsert_companies(companies)

            # 5. Fetch & Upsert Leads
            leads = await self.provider.get_leads()
            items_count += await self.repository.upsert_leads(leads)

            # 6. Fetch & Upsert Tasks & Events
            tasks = await self.provider.get_tasks()
            items_count += await self.repository.upsert_tasks(tasks)

            events = await self.provider.get_events()
            items_count += await self.repository.upsert_events(events)

            # Finish sync log & invalidate dashboard cache
            await self.repository.finish_sync_log(
                log_id=log.id,
                status="success",
                items_synced=items_count
            )
            memory_cache.clear()
            logger.info(f"Sync #{log.id} completed successfully. Synced {items_count} items.")

            return {
                "status": "success",
                "log_id": log.id,
                "items_synced": items_count,
                "message": f"Sincronização concluída com sucesso ({items_count} registros)."
            }

        except Exception as e:
            logger.error(f"Error during CRM sync execution: {e}", exc_info=True)
            await self.repository.finish_sync_log(
                log_id=log.id,
                status="failed",
                items_synced=items_count,
                error_message=str(e)
            )
            return {
                "status": "failed",
                "log_id": log.id,
                "items_synced": items_count,
                "error": str(e),
                "message": "Erro ao executar a sincronização com o Kommo CRM."
            }

    async def get_latest_sync_status(self) -> dict:
        log = await self.repository.get_latest_sync_log()
        if not log:
            return {
                "status": "never_run",
                "last_synced_at": None,
                "items_synced": 0,
                "trigger_type": None
            }
        return {
            "status": log.status,
            "last_synced_at": (log.finished_at or log.started_at).isoformat() if log else None,
            "items_synced": log.items_synced,
            "trigger_type": log.trigger_type,
            "error_message": log.error_message
        }
