import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import Base
from app.services.sync_service import KommoSyncService
from app.services.dashboard_service import DashboardService
from app.providers.kommo_provider import KommoProvider

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
async def test_kommo_sync_service_execution(async_session: AsyncSession):
    provider = KommoProvider(subdomain="demo")
    sync_service = KommoSyncService(async_session, provider=provider)

    result = await sync_service.execute_sync(trigger_type="manual")

    assert result["status"] == "success"
    assert result["items_synced"] > 0
    assert "log_id" in result

    status = await sync_service.get_latest_sync_status()
    assert status["status"] == "success"
    assert status["items_synced"] > 0

@pytest.mark.asyncio
async def test_dashboard_service_metrics(async_session: AsyncSession):
    provider = KommoProvider(subdomain="demo")
    sync_service = KommoSyncService(async_session, provider=provider)
    await sync_service.execute_sync(trigger_type="manual")

    dashboard_service = DashboardService(async_session)

    # Test Overview
    overview = await dashboard_service.get_overview(period="30days")
    assert "total_revenue" in overview
    assert "total_sales" in overview
    assert "overall_ticket" in overview

    # Test Funnel
    funnel = await dashboard_service.get_funnel(period="30days")
    assert "total_leads" in funnel
    assert len(funnel["stages"]) > 0

    # Test Revenue
    revenue = await dashboard_service.get_revenue(period="30days")
    assert revenue["total_revenue"] >= 0
    assert len(revenue["by_unit"]) > 0
    assert len(revenue["by_procedure"]) > 0

    # Test Ranking
    ranking = await dashboard_service.get_ranking(period="30days")
    assert "ranking" in ranking
    assert len(ranking["ranking"]) > 0
