from pydantic import BaseModel, Field
from typing import Optional, Dict

class ConnectUrlRequest(BaseModel):
    subdomain: str = Field(..., description="Kommo subdomain e.g. empresa.kommo.com or empresa")
    company_id: Optional[str] = None

class ConnectUrlResponse(BaseModel):
    auth_url: str
    subdomain: str

class IntegrationStatusResponse(BaseModel):
    id: Optional[str] = None
    company_id: Optional[str] = None
    provider: str = "kommo"
    subdomain: Optional[str] = None
    status: str = "disconnected"
    connected_at: Optional[str] = None
    last_sync: Optional[str] = None
    last_token_refresh: Optional[str] = None
    entity_counts: Dict[str, int] = Field(
        default_factory=lambda: {
            "leads": 0,
            "contacts": 0,
            "companies": 0,
            "users": 0,
            "pipelines": 0,
            "tasks": 0,
            "events": 0
        }
    )

class DisconnectResponse(BaseModel):
    status: str
    message: str

class RefreshTokenResponse(BaseModel):
    status: str
    message: str
    expires_at: Optional[str] = None
