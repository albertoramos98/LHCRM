import logging
import re
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.integrations.kommo.models import CRMIntegration, IntegrationLog

logger = logging.getLogger(__name__)

class KommoOAuthService:
    """
    Service responsible for Kommo CRM OAuth 2.0 flow:
    - Subdomain normalization
    - Authorization URL construction
    - Code exchange for access & refresh tokens
    - Automatic token refresh (expires_at < now())
    - Revocation / Disconnection
    - Detailed audit logging into integration_logs
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def normalize_subdomain(raw_subdomain: str) -> str:
        clean = raw_subdomain.strip().lower()
        clean = re.sub(r"^https?://", "", clean)
        clean = clean.split(".")[0]
        clean = re.sub(r"[^a-z0-9_-]", "", clean)
        return clean or "demo"

    def generate_auth_url(self, raw_subdomain: str, company_id: Optional[str] = None) -> str:
        subdomain = self.normalize_subdomain(raw_subdomain)
        client_id = settings.KOMMO_CLIENT_ID or "demo_client_id"
        redirect_uri = settings.KOMMO_REDIRECT_URI or "http://localhost:8000/api/integrations/kommo/callback"
        state = company_id or "default_company"
        
        return f"https://{subdomain}.kommo.com/oauth?client_id={client_id}&state={state}&mode=popup"

    async def log_event(self, integration_id: str, event_type: str, message: str, status: str = "info"):
        log_entry = IntegrationLog(
            integration_id=integration_id,
            type=event_type,
            message=message,
            status=status
        )
        self.session.add(log_entry)
        await self.session.commit()

    async def exchange_code(self, code: str, raw_subdomain: str, company_id: Optional[str] = None) -> CRMIntegration:
        subdomain = self.normalize_subdomain(raw_subdomain)
        client_id = settings.KOMMO_CLIENT_ID or "demo_client_id"
        client_secret = settings.KOMMO_CLIENT_SECRET or "demo_client_secret"
        redirect_uri = settings.KOMMO_REDIRECT_URI or "http://localhost:8000/api/integrations/kommo/callback"

        # Check for existing integration for company or subdomain
        res = await self.session.execute(
            select(CRMIntegration).where(CRMIntegration.subdomain == subdomain)
        )
        integration = res.scalar_one_or_none()

        now = datetime.utcnow()

        if subdomain == "demo" or code.startswith("demo_"):
            access_token = f"demo_access_token_{subdomain}"
            refresh_token = f"demo_refresh_token_{subdomain}"
            expires_at = now + timedelta(seconds=86400) # 24h
        else:
            async with httpx.AsyncClient() as client:
                token_url = f"https://{subdomain}.kommo.com/oauth2/access_token"
                payload = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri
                }
                response = await client.post(token_url, json=payload)
                if response.status_code != 200:
                    err_msg = f"OAuth Token Exchange failed ({response.status_code}): {response.text}"
                    logger.error(err_msg)
                    if integration:
                        await self.log_event(integration.id, "oauth_error", err_msg, status="error")
                    raise ValueError(err_msg)

                data = response.json()
                access_token = data["access_token"]
                refresh_token = data["refresh_token"]
                expires_in = data.get("expires_in", 86400)
                expires_at = now + timedelta(seconds=expires_in)

        if not integration:
            integration = CRMIntegration(
                company_id=company_id or "default_company",
                provider="kommo",
                subdomain=subdomain,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                connected_at=now,
                status="connected"
            )
            self.session.add(integration)
        else:
            integration.access_token = access_token
            integration.refresh_token = refresh_token
            integration.expires_at = expires_at
            integration.connected_at = now
            integration.status = "connected"
            integration.updated_at = now

        await self.session.commit()
        await self.session.refresh(integration)

        await self.log_event(
            integration.id,
            "connection_established",
            f"Integração com Kommo CRM ({subdomain}) estabelecida com sucesso.",
            status="success"
        )
        return integration

    async def get_valid_token(self, integration_id: str) -> str:
        """
        Retrieves access_token for integration.
        Checks if expires_at < now(), and automatically executes token refresh if expired!
        """
        res = await self.session.execute(
            select(CRMIntegration).where(CRMIntegration.id == integration_id)
        )
        integration = res.scalar_one_or_none()
        if not integration or integration.status != "connected":
            raise ValueError("Integração Kommo CRM não encontrada ou desconectada.")

        now = datetime.utcnow()
        if integration.expires_at and integration.expires_at < (now + timedelta(minutes=5)):
            logger.info(f"Access token for integration {integration.id} is expired. Triggering auto-refresh...")
            integration = await self.refresh_token(integration.id)

        return integration.access_token

    async def refresh_token(self, integration_id: str) -> CRMIntegration:
        res = await self.session.execute(
            select(CRMIntegration).where(CRMIntegration.id == integration_id)
        )
        integration = res.scalar_one_or_none()
        if not integration:
            raise ValueError("Integração não encontrada.")

        now = datetime.utcnow()

        if integration.subdomain == "demo" or (integration.refresh_token and integration.refresh_token.startswith("demo_")):
            new_access_token = f"demo_access_token_{integration.subdomain}_refreshed"
            new_refresh_token = f"demo_refresh_token_{integration.subdomain}_refreshed"
            new_expires_at = now + timedelta(seconds=86400)
        else:
            async with httpx.AsyncClient() as client:
                token_url = f"https://{integration.subdomain}.kommo.com/oauth2/access_token"
                payload = {
                    "client_id": integration.client_id or settings.KOMMO_CLIENT_ID,
                    "client_secret": integration.client_secret or settings.KOMMO_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": integration.refresh_token,
                    "redirect_uri": integration.redirect_uri or settings.KOMMO_REDIRECT_URI
                }
                response = await client.post(token_url, json=payload)
                if response.status_code != 200:
                    err_msg = f"Falha ao renovar refresh token ({response.status_code}): {response.text}"
                    logger.error(err_msg)
                    integration.status = "expired"
                    await self.session.commit()
                    await self.log_event(integration.id, "oauth_error", err_msg, status="error")
                    raise ValueError(err_msg)

                data = response.json()
                new_access_token = data["access_token"]
                new_refresh_token = data["refresh_token"]
                expires_in = data.get("expires_in", 86400)
                new_expires_at = now + timedelta(seconds=expires_in)

        integration.access_token = new_access_token
        integration.refresh_token = new_refresh_token
        integration.expires_at = new_expires_at
        integration.status = "connected"
        integration.updated_at = now

        await self.session.commit()
        await self.session.refresh(integration)

        await self.log_event(
            integration.id,
            "token_refreshed",
            "Access token renovado com sucesso via Refresh Token.",
            status="success"
        )
        return integration

    async def disconnect(self, integration_id: str) -> dict:
        res = await self.session.execute(
            select(CRMIntegration).where(CRMIntegration.id == integration_id)
        )
        integration = res.scalar_one_or_none()
        if not integration:
            return {"status": "error", "message": "Integração não encontrada."}

        integration.status = "disconnected"
        integration.access_token = None
        integration.refresh_token = None
        integration.updated_at = datetime.utcnow()

        await self.session.commit()

        await self.log_event(
            integration.id,
            "connection_disconnected",
            f"Integração Kommo CRM ({integration.subdomain}) desconectada pelo usuário.",
            status="info"
        )

        return {"status": "success", "message": "Integração desconectada com sucesso."}
