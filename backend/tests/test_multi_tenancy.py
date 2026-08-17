import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import Base, User, Organization, OrganizationMember, Lead, Pipeline, LeadStatus
from app.core.security import get_password_hash, create_access_token
from app.core.database import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        # 1. Create Organization A
        org_a = Organization(id=1, name="Clínica Alpha", slug="alpha", is_active=True)
        # 2. Create Organization B
        org_b = Organization(id=2, name="Clínica Beta", slug="beta", is_active=True)
        session.add_all([org_a, org_b])
        await session.flush()

        # Users
        user_a = User(id=1, organization_id=1, name="Admin Alpha", email="admin@alpha.com", hashed_password=get_password_hash("Pass123!"), role="Admin", is_active=True)
        user_b = User(id=2, organization_id=2, name="Admin Beta", email="admin@beta.com", hashed_password=get_password_hash("Pass123!"), role="Admin", is_active=True)
        session.add_all([user_a, user_b])
        await session.flush()

        session.add(OrganizationMember(organization_id=1, user_id=1, role="Admin"))
        session.add(OrganizationMember(organization_id=2, user_id=2, role="Admin"))

        # Pipelines & Statuses
        pipe_a = Pipeline(id=1, organization_id=1, name="Funil Alpha")
        pipe_b = Pipeline(id=2, organization_id=2, name="Funil Beta")
        session.add_all([pipe_a, pipe_b])
        await session.flush()

        status_a = LeadStatus(id=1, organization_id=1, pipeline_id=1, name="Vendido Alpha")
        status_b = LeadStatus(id=2, organization_id=2, pipeline_id=2, name="Vendido Beta")
        session.add_all([status_a, status_b])
        await session.flush()

        # Leads for Org A (Total revenue: R$ 50.000)
        lead_a1 = Lead(
            id=1, organization_id=1, external_id=101, name="Lead Alpha 1", price=20000.0,
            pipeline_id=1, status_id=1, closed_at=datetime.now(timezone.utc), unidade="Matriz Alpha"
        )
        lead_a2 = Lead(
            id=2, organization_id=1, external_id=102, name="Lead Alpha 2", price=30000.0,
            pipeline_id=1, status_id=1, closed_at=datetime.now(timezone.utc), unidade="Matriz Alpha"
        )

        # Leads for Org B (Total revenue: R$ 80.000)
        lead_b1 = Lead(
            id=3, organization_id=2, external_id=201, name="Lead Beta 1", price=80000.0,
            pipeline_id=2, status_id=2, closed_at=datetime.now(timezone.utc), unidade="Matriz Beta"
        )
        session.add_all([lead_a1, lead_a2, lead_b1])
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def client(test_db_session: AsyncSession):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_tenant_a_isolation(client: AsyncClient):
    token_a = create_access_token(subject=1, role="Admin", organization_id=1)
    res = await client.get("/api/dashboard/revenue", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200
    data = res.json()

    # Must only see Org A revenue (50,000)
    assert data["total_revenue"] == 50000.0
    assert data["total_sales"] == 2
    assert len(data["by_unit"]) == 1
    assert data["by_unit"][0]["unidade"] == "Matriz Alpha"

@pytest.mark.asyncio
async def test_tenant_b_isolation(client: AsyncClient):
    token_b = create_access_token(subject=2, role="Admin", organization_id=2)
    res = await client.get("/api/dashboard/revenue", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 200
    data = res.json()

    # Must only see Org B revenue (80,000)
    assert data["total_revenue"] == 80000.0
    assert data["total_sales"] == 1
    assert len(data["by_unit"]) == 1
    assert data["by_unit"][0]["unidade"] == "Matriz Beta"

@pytest.mark.asyncio
async def test_cross_tenant_access_blocked(client: AsyncClient):
    # User from Org A tries to access Org B data by sending X-Organization-ID: 2
    token_a = create_access_token(subject=1, role="Admin", organization_id=1)
    res = await client.get(
        "/api/dashboard/revenue",
        headers={
            "Authorization": f"Bearer {token_a}",
            "X-Organization-ID": "2"
        }
    )
    assert res.status_code == 403
    assert "Acesso negado" in res.json()["detail"]
