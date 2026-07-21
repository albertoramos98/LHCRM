from pydantic import BaseModel
from typing import Optional

class SyncTriggerResponse(BaseModel):
    status: str
    log_id: int
    items_synced: int
    message: str
    error: Optional[str] = None

class SyncStatusResponse(BaseModel):
    status: str
    last_synced_at: Optional[str] = None
    items_synced: int
    trigger_type: Optional[str] = None
    error_message: Optional[str] = None
