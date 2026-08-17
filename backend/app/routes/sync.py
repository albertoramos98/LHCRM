from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_tenant_context, TenantContext, rate_limit_sync, require_role
from app.services.sync_service import KommoSyncService
from app.schemas.sync import SyncTriggerResponse, SyncStatusResponse

router = APIRouter(prefix="/api/sync", tags=["CRM Synchronization"])

@router.post("/now", response_model=SyncTriggerResponse)
async def sync_now(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_role(["Owner", "Admin", "Gerente"]))
):
    """
    Trigger immediate manual synchronization from Kommo CRM to local PostgreSQL database
    for the authenticated user's organization.
    """
    rate_limit_sync(request)
    service = KommoSyncService(db, organization_id=tenant.organization_id)
    result = await service.execute_sync(trigger_type="manual")
    return SyncTriggerResponse(**result)

@router.get("/status", response_model=SyncStatusResponse)
async def sync_status(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Check the latest synchronization status and timestamp for the tenant organization.
    """
    service = KommoSyncService(db, organization_id=tenant.organization_id)
    status_data = await service.get_latest_sync_status()
    return SyncStatusResponse(**status_data)
