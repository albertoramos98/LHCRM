import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.models.domain import Base, Organization, User, Pipeline, LeadStatus, Lead, Contact, Task
from app.integrations.kommo.models import CRMIntegration, IntegrationLog
from app.integrations.kommo.oauth import KommoOAuthService
from app.integrations.kommo.sync import KommoIntegrationSyncService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        # Create 2 distinct organizations for multi-tenant isolation tests
        org1 = Organization(id=1, name="Clínica Jardins", slug="jardins", is_active=True)
        org2 = Organization(id=2, name="Clínica Barra", slug="barra", is_active=True)
        session.add_all([org1, org2])
        await session.commit()
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_kommo_oauth_full_cycle(async_session: AsyncSession):
    """
    Testes de integração: Ciclo completo OAuth Kommo CRM
    1. Normalização de subdomínio
    2. Troca de authorization code
    3. Validação e persistência de tokens
    4. Auto-refresh de tokens expirados
    """
    oauth_service = KommoOAuthService(async_session, organization_id=1)

    # 1. Normalização de Subdomínio
    assert oauth_service.normalize_subdomain("https://minhaclinica.kommo.com/") == "minhaclinica"
    assert oauth_service.normalize_subdomain("clinica_saude.amocrm.com") == "clinica_saude"
    assert oauth_service.normalize_subdomain("   demo_clinica   ") == "demo_clinica"

    # 2. Exchange Code (usando prefixo demo_ para ambiente de teste isolado)
    integration = await oauth_service.exchange_code(
        code="demo_auth_code_kommo_123",
        raw_subdomain="demo_estetica.kommo.com",
        company_id="comp_1"
    )

    assert integration.id is not None
    assert integration.organization_id == 1
    assert integration.subdomain == "demo_estetica"
    assert integration.status == "connected"
    assert integration.access_token is not None
    assert integration.refresh_token is not None

    # 3. Valid Token Retrieval
    token = await oauth_service.get_valid_token(integration.id)
    assert token is not None
    assert len(token) > 5

    # 4. Expiration and Auto-Refresh
    integration.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    await async_session.commit()

    refreshed_token = await oauth_service.get_valid_token(integration.id)
    assert refreshed_token is not None
    assert "refreshed" in refreshed_token
    assert integration.status == "connected"

@pytest.mark.asyncio
async def test_kommo_sync_execution_and_entity_mapping(async_session: AsyncSession):
    """
    Testes de integração: Sincronização e Mapeamento de Entidades
    1. Sincroniza pipelines e status
    2. Sincroniza leads com campos customizados (unidade, procedimento, origem, valor)
    3. Registra logs de auditoria
    4. Atualiza contadores e estatísticas
    """
    oauth_service = KommoOAuthService(async_session, organization_id=1)
    integration = await oauth_service.exchange_code(
        code="demo_sync_test_code",
        raw_subdomain="demo.kommo.com"
    )

    sync_service = KommoIntegrationSyncService(async_session, organization_id=1)
    result = await sync_service.sync_integration(integration.id, trigger_type="manual")

    assert result["status"] == "success"
    assert result["items_synced"] > 0

    # Verify entities stored
    stats = await sync_service.get_integration_status_and_stats(company_id=integration.company_id)
    assert stats["status"] == "connected"
    assert stats["entity_counts"]["leads"] > 0
    assert stats["entity_counts"]["pipelines"] > 0

    # Verify logs created
    logs_res = await async_session.execute(
        select(IntegrationLog).where(IntegrationLog.organization_id == 1)
    )
    logs = list(logs_res.scalars().all())
    assert len(logs) >= 2
    types = [l.type for l in logs]
    assert "sync_started" in types
    assert "sync_completed" in types

@pytest.mark.asyncio
async def test_kommo_multi_tenant_isolation(async_session: AsyncSession):
    """
    Testes de integração: Isolamento Multi-tenant
    Garante que uma organização não consegue sincronizar ou acessar dados da integração de outra.
    """
    oauth_org1 = KommoOAuthService(async_session, organization_id=1)
    integ_org1 = await oauth_org1.exchange_code(
        code="demo_code_org1",
        raw_subdomain="demo_org1.kommo.com"
    )

    # Org 2 attempts to sync Org 1 integration -> Should fail with ValueError
    sync_org2 = KommoIntegrationSyncService(async_session, organization_id=2)
    with pytest.raises(ValueError, match="não encontrada ou inativa"):
        await sync_org2.sync_integration(integ_org1.id)

@pytest.mark.asyncio
async def test_kommo_disconnect_and_reconnect(async_session: AsyncSession):
    """
    Testes de integração: Desconexão e Reconexão Segura
    """
    oauth_service = KommoOAuthService(async_session, organization_id=1)
    integration = await oauth_service.exchange_code(
        code="demo_reconnect_code",
        raw_subdomain="demo_clinica_alpha.kommo.com"
    )

    # Disconnect
    integration.status = "disconnected"
    integration.access_token = None
    integration.refresh_token = None
    await async_session.commit()

    sync_service = KommoIntegrationSyncService(async_session, organization_id=1)
    with pytest.raises(ValueError, match="não encontrada ou inativa"):
        await sync_service.sync_integration(integration.id)

    # Reconnect
    reconnected = await oauth_service.exchange_code(
        code="demo_new_code_123",
        raw_subdomain="demo_clinica_alpha.kommo.com"
    )
    assert reconnected.status == "connected"
    assert reconnected.access_token is not None
