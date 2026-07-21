import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import Base
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
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_subdomain_normalization(async_session: AsyncSession):
    oauth_service = KommoOAuthService(async_session)

    assert oauth_service.normalize_subdomain("empresa.kommo.com") == "empresa"
    assert oauth_service.normalize_subdomain("https://minha-clinica.amocrm.com") == "minha-clinica"
    assert oauth_service.normalize_subdomain("  SAUDE_E_VIDA  ") == "saude_e_vida"

@pytest.mark.asyncio
async def test_oauth_exchange_and_auto_refresh(async_session: AsyncSession):
    oauth_service = KommoOAuthService(async_session)

    # 1. Exchange Code
    integration = await oauth_service.exchange_code(
        code="demo_test_code",
        raw_subdomain="clinica.kommo.com",
        company_id="comp_123"
    )

    assert integration.status == "connected"
    assert integration.subdomain == "clinica"
    assert integration.access_token is not None
    assert integration.refresh_token is not None

    # 2. Simulate expired token
    integration.expires_at = datetime.utcnow() - timedelta(minutes=10)
    await async_session.commit()

    # 3. Retrieve valid token (should trigger auto-refresh)
    valid_token = await oauth_service.get_valid_token(integration.id)
    assert "refreshed" in valid_token
    assert integration.status == "connected"

@pytest.mark.asyncio
async def test_integration_sync_and_stats(async_session: AsyncSession):
    oauth_service = KommoOAuthService(async_session)
    integration = await oauth_service.exchange_code(
        code="demo_test_code",
        raw_subdomain="demo.kommo.com"
    )

    sync_service = KommoIntegrationSyncService(async_session)
    sync_result = await sync_service.sync_integration(integration.id, trigger_type="manual")

    assert sync_result["status"] == "success"
    assert sync_result["items_synced"] > 0

    stats = await sync_service.get_integration_status_and_stats(company_id=integration.company_id)
    assert stats["status"] == "connected"
    assert stats["entity_counts"]["leads"] > 0
