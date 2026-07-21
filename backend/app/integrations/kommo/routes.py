from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.integrations.kommo.oauth import KommoOAuthService
from app.integrations.kommo.sync import KommoIntegrationSyncService
from app.integrations.kommo.schemas import (
    ConnectUrlResponse, IntegrationStatusResponse, DisconnectResponse, RefreshTokenResponse
)

router = APIRouter(prefix="/api/integrations/kommo", tags=["Kommo CRM Integration"])

@router.get("/connect", response_model=ConnectUrlResponse)
async def get_connect_url(
    subdomain: str = Query(..., description="Subdomínio da conta Kommo (ex: empresa.kommo.com)"),
    company_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates Kommo OAuth 2.0 Authorization URL for a client subdomain.
    """
    oauth_service = KommoOAuthService(db)
    clean_subdomain = oauth_service.normalize_subdomain(subdomain)
    auth_url = oauth_service.generate_auth_url(clean_subdomain, company_id)
    return ConnectUrlResponse(auth_url=auth_url, subdomain=clean_subdomain)

@router.get("/callback")
async def oauth_callback(
    code: Optional[str] = Query(None),
    referer: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    subdomain: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Callback URL specified in Kommo OAuth Integration configuration.
    Exchanges code for access & refresh tokens, saves to Supabase PostgreSQL, and triggers initial sync.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Autorização negada pelo Kommo: {error}"
        )

    if not code:
        # Fallback to mock code if connecting in demo mode
        code = "demo_code_authorization"

    target_subdomain = subdomain or referer or "demo"
    oauth_service = KommoOAuthService(db)

    try:
        integration = await oauth_service.exchange_code(
            code=code,
            raw_subdomain=target_subdomain,
            company_id=state
        )

        # Trigger initial background sync
        sync_service = KommoIntegrationSyncService(db)
        await sync_service.sync_integration(integration.id, trigger_type="automatic")

        # Redirect to frontend dashboard with success query param
        return RedirectResponse(url="http://localhost:3000/?integration=success", status_code=302)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar OAuth Callback: {str(e)}"
        )

@router.get("/status", response_model=IntegrationStatusResponse)
async def get_integration_status(
    company_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns active integration status, timestamps, and synced entity counts.
    Never exposes access_token or client_secret to the frontend.
    """
    sync_service = KommoIntegrationSyncService(db)
    status_data = await sync_service.get_integration_status_and_stats(company_id=company_id)
    return IntegrationStatusResponse(**status_data)

@router.post("/disconnect", response_model=DisconnectResponse)
async def disconnect_integration(
    company_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Revokes and disconnects active Kommo CRM integration.
    """
    sync_service = KommoIntegrationSyncService(db)
    status_data = await sync_service.get_integration_status_and_stats(company_id=company_id)
    if not status_data["id"]:
        return DisconnectResponse(status="warning", message="Nenhuma integração ativa encontrada.")

    oauth_service = KommoOAuthService(db)
    result = await oauth_service.disconnect(status_data["id"])
    return DisconnectResponse(**result)

@router.post("/refresh-token", response_model=RefreshTokenResponse)
async def manual_refresh_token(
    company_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually triggers OAuth token refresh.
    """
    sync_service = KommoIntegrationSyncService(db)
    status_data = await sync_service.get_integration_status_and_stats(company_id=company_id)
    if not status_data["id"]:
        raise HTTPException(status_code=400, detail="Nenhuma integração ativa encontrada.")

    oauth_service = KommoOAuthService(db)
    updated_integration = await oauth_service.refresh_token(status_data["id"])
    
    return RefreshTokenResponse(
        status="success",
        message="Token renovado com sucesso.",
        expires_at=updated_integration.expires_at.isoformat() if updated_integration.expires_at else None
    )

@router.post("/sync")
async def trigger_integration_sync(
    company_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually triggers full data synchronization from Kommo CRM to Supabase.
    """
    sync_service = KommoIntegrationSyncService(db)
    status_data = await sync_service.get_integration_status_and_stats(company_id=company_id)
    if not status_data["id"]:
        raise HTTPException(status_code=400, detail="Integração inativa ou não configurada.")

    return await sync_service.sync_integration(status_data["id"], trigger_type="manual")
