from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.sync_service import KommoSyncService
from app.schemas.sync import SyncTriggerResponse, SyncStatusResponse

router = APIRouter(prefix="/api/sync", tags=["CRM Synchronization"])

@router.post("/now", response_model=SyncTriggerResponse)
async def sync_now(db: AsyncSession = Depends(get_db)):
    """
    Trigger immediate manual synchronization from Kommo CRM to local PostgreSQL database.
    """
    service = KommoSyncService(db)
    result = await service.execute_sync(trigger_type="manual")
    return SyncTriggerResponse(**result)

@router.get("/status", response_model=SyncStatusResponse)
async def sync_status(db: AsyncSession = Depends(get_db)):
    """
    Check the latest synchronization status and timestamp.
    """
    service = KommoSyncService(db)
    status_data = await service.get_latest_sync_status()
    return SyncStatusResponse(**status_data)
