import logging
import re
import hmac
import hashlib
import base64
import json
import secrets
import time
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.config import settings
from app.integrations.kommo.models import CRMIntegration, IntegrationLog

logger = logging.getLogger(__name__)

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class KommoOAuthService:
    """
    Service responsible for Kommo CRM OAuth 2.0 flow per tenant organization:
    - Subdomain normalization
    - Cryptographically signed OAuth state generation and validation (HMAC-SHA256)
    - Authorization URL construction
    - Code exchange for access & refresh tokens
    - Automatic token refresh
    - Revocation / Disconnection
    - Detailed audit logging
    """

    def __init__(self, session: AsyncSession, organization_id: int = 1):
        self.session = session
        self.organization_id = organization_id

    @staticmethod
    def normalize_subdomain(raw_subdomain: str) -> str:
        clean = raw_subdomain.strip().lower()
        clean = re.sub(r"^https?://", "", clean)
        clean = clean.split(".")[0]
        clean = re.sub(r"[^a-z0-9_-]", "", clean)
        return clean or "demo"

    def create_oauth_state(self, company_id: Optional[str] = None) -> str:
        """
        Creates a cryptographically signed OAuth state token containing:
        - organization_id
        - nonce (cryptographic random salt)
        - expiration timestamp (10 minutes TTL)
        Format: base64url(payload) + '.' + hmac_sha256(raw_payload, SECRET_KEY)
        """
        payload = {
            "org_id": self.organization_id,
            "company_id": company_id or f"org_{self.organization_id}",
            "nonce": secrets.token_hex(16),
            "exp": int(time.time()) + 600 # 10 minutes validity
        }
        raw_json = json.dumps(payload, sort_keys=True)
        raw_b64 = base64.urlsafe_b64encode(raw_json.encode()).decode()
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            raw_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{raw_b64}.{signature}"

    @staticmethod
    def verify_oauth_state(state: str) -> Dict[str, Any]:
        """
        Verifies the cryptographic HMAC-SHA256 signature and expiration of the OAuth state.
        Raises ValueError on any tampering, signature mismatch, or expiration.
        """
        if not state or "." not in state:
            raise ValueError("State OAuth ausente ou com formato inválido.")

        parts = state.split(".")
        if len(parts) != 2:
            raise ValueError("Formato de token de state OAuth inválido.")

        raw_b64, signature = parts[0], parts[1]

        # Verify HMAC signature
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            raw_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError("Assinatura criptográfica do state OAuth inválida ou adulterada.")

        # Decode payload
        try:
            raw_json = base64.urlsafe_b64decode(raw_b64.encode()).decode()
            payload = json.loads(raw_json)
        except Exception:
            raise ValueError("Payload do state OAuth corrompido.")

        # Check expiration
        exp = payload.get("exp", 0)
        if time.time() > exp:
            raise ValueError("O token de state OAuth expirou. Por favor, reinicie o fluxo de autorização.")

        org_id = payload.get("org_id")
        if not org_id:
            raise ValueError("State OAuth sem identificador de organização.")

        return payload

    async def generate_auth_url(
        self,
        raw_subdomain: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> str:
        subdomain = self.normalize_subdomain(raw_subdomain)
        cid = client_id.strip() if client_id and client_id.strip() else (settings.KOMMO_CLIENT_ID or "demo_client_id")
        csecret = client_secret.strip() if client_secret and client_secret.strip() else (settings.KOMMO_CLIENT_SECRET or "demo_client_secret")
        redirect_uri = settings.KOMMO_REDIRECT_URI or "http://localhost:8000/api/integrations/kommo/callback"
        
        # Cryptographically signed state
        state = self.create_oauth_state(company_id=company_id)

        # Persist or update pending integration with provided credentials scoped to organization
        res = await self.session.execute(
            select(CRMIntegration).where(
                CRMIntegration.organization_id == self.organization_id,
                CRMIntegration.subdomain == subdomain
            )
        )
        integration = res.scalar_one_or_none()

        if not integration:
            integration = CRMIntegration(
                organization_id=self.organization_id,
                company_id=company_id or f"comp_{self.organization_id}",
                provider="kommo",
                subdomain=subdomain,
                client_id=cid,
                client_secret=csecret,
                redirect_uri=redirect_uri,
                status="pending"
            )
            self.session.add(integration)
        else:
            integration.client_id = cid
            integration.client_secret = csecret
            integration.redirect_uri = redirect_uri
            if integration.status != "connected":
                integration.status = "pending"
            integration.updated_at = utc_now()

        await self.session.commit()
        
        return f"https://{subdomain}.kommo.com/oauth?client_id={cid}&state={state}&mode=popup"

    async def log_event(self, integration_id: str, event_type: str, message: str, status: str = "info"):
        log_entry = IntegrationLog(
            organization_id=self.organization_id,
            integration_id=integration_id,
            type=event_type,
            message=message,
            status=status,
            created_at=utc_now()
        )
        self.session.add(log_entry)
        await self.session.commit()

    async def exchange_code(self, code: str, raw_subdomain: str, company_id: Optional[str] = None) -> CRMIntegration:
        subdomain = self.normalize_subdomain(raw_subdomain)

        # Check for existing integration for organization
        res = await self.session.execute(
            select(CRMIntegration).where(
                CRMIntegration.organization_id == self.organization_id,
                CRMIntegration.subdomain == subdomain
            )
        )
        integration = res.scalar_one_or_none()

        client_id = (integration.client_id if integration and integration.client_id else settings.KOMMO_CLIENT_ID) or "demo_client_id"
        client_secret = (integration.client_secret if integration and integration.client_secret else settings.KOMMO_CLIENT_SECRET) or "demo_client_secret"
        redirect_uri = (integration.redirect_uri if integration and integration.redirect_uri else settings.KOMMO_REDIRECT_URI) or "http://localhost:8000/api/integrations/kommo/callback"

        now = utc_now()

        if subdomain == "demo" or code.startswith("demo_"):
            access_token = f"demo_access_token_{subdomain}"
            refresh_token = f"demo_refresh_token_{subdomain}"
            expires_at = now + timedelta(seconds=86400) # 24h
        else:
            async with httpx.AsyncClient(timeout=15.0) as client:
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
                    err_msg = f"OAuth Token Exchange failed ({response.status_code})"
                    logger.error(f"{err_msg}: {response.text}")
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
                organization_id=self.organization_id,
                company_id=company_id or f"comp_{self.organization_id}",
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
            integration.client_id = client_id
            integration.client_secret = client_secret
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
        Retrieves access_token for integration scoped to organization.
        Checks if expires_at < now(), and automatically executes token refresh if expired!
        """
        res = await self.session.execute(
            select(CRMIntegration).where(
                CRMIntegration.id == integration_id,
                CRMIntegration.organization_id == self.organization_id
            )
        )
        integration = res.scalar_one_or_none()
        if not integration or integration.status != "connected":
            raise ValueError("Integração Kommo CRM não encontrada ou desconectada.")

        now = utc_now()
        exp_aware = integration.expires_at.replace(tzinfo=timezone.utc) if (integration.expires_at and integration.expires_at.tzinfo is None) else integration.expires_at

        if exp_aware and exp_aware < (now + timedelta(minutes=5)):
            logger.info(f"Access token for integration {integration.id} is expired. Triggering auto-refresh...")
            integration = await self.refresh_token(integration.id)

        return integration.access_token

    async def refresh_token(self, integration_id: str) -> CRMIntegration:
        res = await self.session.execute(
            select(CRMIntegration).where(
                CRMIntegration.id == integration_id,
                CRMIntegration.organization_id == self.organization_id
            )
        )
        integration = res.scalar_one_or_none()
        if not integration:
            raise ValueError("Integração não encontrada.")

        now = utc_now()

        if integration.subdomain == "demo" or (integration.refresh_token and integration.refresh_token.startswith("demo_")):
            new_access_token = f"demo_access_token_{integration.subdomain}_refreshed"
            new_refresh_token = f"demo_refresh_token_{integration.subdomain}_refreshed"
            new_expires_at = now + timedelta(seconds=86400)
        else:
            async with httpx.AsyncClient(timeout=15.0) as client:
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
                    err_msg = f"Falha ao renovar refresh token ({response.status_code})"
                    logger.error(f"{err_msg}: {response.text}")
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
            select(CRMIntegration).where(
                CRMIntegration.id == integration_id,
                CRMIntegration.organization_id == self.organization_id
            )
        )
        integration = res.scalar_one_or_none()
        if not integration:
            return {"status": "error", "message": "Integração não encontrada."}

        integration.status = "disconnected"
        integration.access_token = None
        integration.refresh_token = None
        integration.updated_at = utc_now()

        await self.session.commit()

        await self.log_event(
            integration.id,
            "connection_disconnected",
            f"Integração Kommo CRM ({integration.subdomain}) desconectada pelo usuário.",
            status="info"
        )

        return {"status": "success", "message": "Integração desconectada com sucesso."}
