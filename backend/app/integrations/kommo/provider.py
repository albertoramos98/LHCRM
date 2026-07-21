import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.kommo_provider import KommoProvider
from app.integrations.kommo.oauth import KommoOAuthService

logger = logging.getLogger(__name__)

class KommoIntegrationProvider(KommoProvider):
    """
    Subclass of KommoProvider that dynamically resolves OAuth tokens for a specific CRMIntegration.
    Automatically verifies token expiration and triggers refresh prior to API requests.
    """

    def __init__(self, subdomain: str, access_token: str):
        super().__init__(subdomain=subdomain, token=access_token)

    @classmethod
    async def create_for_integration(cls, session: AsyncSession, integration_id: str) -> "KommoIntegrationProvider":
        oauth_service = KommoOAuthService(session)
        token = await oauth_service.get_valid_token(integration_id)
        
        # Get subdomain
        from app.integrations.kommo.models import CRMIntegration
        from sqlalchemy import select
        res = await session.execute(select(CRMIntegration).where(CRMIntegration.id == integration_id))
        integration = res.scalar_one()

        return cls(subdomain=integration.subdomain, access_token=token)
