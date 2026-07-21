import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.services.sync_service import KommoSyncService
from app.integrations.kommo.provider import KommoIntegrationProvider
from app.integrations.kommo.models import CRMIntegration, IntegrationLog
from app.models.domain import Lead, Contact, Company, User, Pipeline, Task, Event

logger = logging.getLogger(__name__)

class KommoIntegrationSyncService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_integration(self, integration_id: str, trigger_type: str = "manual") -> dict:
        res = await self.session.execute(
            select(CRMIntegration).where(CRMIntegration.id == integration_id)
        )
        integration = res.scalar_one_or_none()
        if not integration or integration.status != "connected":
            raise ValueError("Integração não encontrada ou inativa.")

        # Log sync started
        start_log = IntegrationLog(
            integration_id=integration.id,
            type="sync_started",
            message=f"Sincronização de dados iniciada ({trigger_type}).",
            status="info"
        )
        self.session.add(start_log)
        await self.session.commit()

        try:
            # Instantiate provider with fresh token
            provider = await KommoIntegrationProvider.create_for_integration(self.session, integration.id)
            core_sync = KommoSyncService(self.session, provider=provider)

            result = await core_sync.execute_sync(trigger_type=trigger_type)

            # Update integration last_sync timestamp
            now = datetime.utcnow()
            integration.last_sync = now
            integration.updated_at = now
            await self.session.commit()

            # Log sync completed
            complete_log = IntegrationLog(
                integration_id=integration.id,
                type="sync_completed",
                message=f"Sincronização concluída com sucesso ({result['items_synced']} registros).",
                status="success"
            )
            self.session.add(complete_log)
            await self.session.commit()

            return {
                "status": "success",
                "integration_id": integration.id,
                "items_synced": result["items_synced"],
                "last_sync": now.isoformat(),
                "message": f"Sincronização realizada com sucesso para {integration.subdomain}."
            }

        except Exception as e:
            logger.error(f"Error during integration sync: {e}", exc_info=True)
            err_log = IntegrationLog(
                integration_id=integration.id,
                type="api_error",
                message=f"Erro durante sincronização: {str(e)}",
                status="error"
            )
            self.session.add(err_log)
            await self.session.commit()
            raise e

    async def get_integration_status_and_stats(self, company_id: Optional[str] = None) -> dict:
        query = select(CRMIntegration)
        if company_id:
            query = query.where(CRMIntegration.company_id == company_id)
        else:
            query = query.order_by(CRMIntegration.created_at.desc()).limit(1)

        res = await self.session.execute(query)
        integration = res.scalar_one_or_none()

        if not integration:
            return {
                "id": None,
                "company_id": company_id or "default_company",
                "provider": "kommo",
                "subdomain": None,
                "status": "disconnected",
                "connected_at": None,
                "last_sync": None,
                "last_token_refresh": None,
                "entity_counts": {
                    "leads": 0, "contacts": 0, "companies": 0,
                    "users": 0, "pipelines": 0, "tasks": 0, "events": 0
                }
            }

        # Query entity counts from Supabase PostgreSQL
        leads_cnt = (await self.session.execute(select(func.count(Lead.id)))).scalar_one()
        contacts_cnt = (await self.session.execute(select(func.count(Contact.id)))).scalar_one()
        companies_cnt = (await self.session.execute(select(func.count(Company.id)))).scalar_one()
        users_cnt = (await self.session.execute(select(func.count(User.id)))).scalar_one()
        pipelines_cnt = (await self.session.execute(select(func.count(Pipeline.id)))).scalar_one()
        tasks_cnt = (await self.session.execute(select(func.count(Task.id)))).scalar_one()
        events_cnt = (await self.session.execute(select(func.count(Event.id)))).scalar_one()

        return {
            "id": integration.id,
            "company_id": integration.company_id,
            "provider": integration.provider,
            "subdomain": integration.subdomain,
            "status": integration.status,
            "connected_at": integration.connected_at.isoformat() if integration.connected_at else None,
            "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
            "last_token_refresh": integration.updated_at.isoformat() if integration.updated_at else None,
            "entity_counts": {
                "leads": leads_cnt,
                "contacts": contacts_cnt,
                "companies": companies_cnt,
                "users": users_cnt,
                "pipelines": pipelines_cnt,
                "tasks": tasks_cnt,
                "events": events_cnt
            }
        }
