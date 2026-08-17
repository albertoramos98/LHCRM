import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import Base, User, Organization, OrganizationMember
from app.integrations.kommo.models import CRMIntegration
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
        # Org 1 and Org 2
        org1 = Organization(id=1, name="Empresa 1", slug="empresa-1", is_active=True)
        org2 = Organization(id=2, name="Empresa 2", slug="empresa-2", is_active=True)
        session.add_all([org1, org2])
        await session.flush()

        user1 = User(id=1, organization_id=1, name="User Org 1", email="user@org1.com", hashed_password=get_password_hash("Pass123!"), role="Admin", is_active=True)
        user2 = User(id=2, organization_id=2, name="User Org 2", email="user@org2.com", hashed_password=get_password_hash("Pass123!"), role="Admin", is_active=True)
        session.add_all([user1, user2])
        await session.flush()

        session.add(OrganizationMember(organization_id=1, user_id=1, role="Admin"))
        session.add(OrganizationMember(organization_id=2, user_id=2, role="Admin"))

        # Org 2 has a connected Kommo integration
        int_org2 = CRMIntegration(
            id="int_org2_secret",
            organization_id=2,
            company_id="comp_2",
            provider="kommo",
            subdomain="org2subdomain",
            client_id="cid_org2",
            client_secret="csecret_org2",
            access_token="token_org2_secret",
            status="connected"
        )
        session.add(int_org2)
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
async def test_idor_prevented_on_integration_status(client: AsyncClient):
    # Org 1 user asks for integration status
    token1 = create_access_token(subject=1, role="Admin", organization_id=1)
    res = await client.get("/api/integrations/kommo/status", headers={"Authorization": f"Bearer {token1}"})
    assert res.status_code == 200
    data = res.json()

    # Must NOT see Org 2's connected integration
    assert data["status"] == "disconnected"
    assert data["id"] is None
    assert data["subdomain"] is None

@pytest.mark.asyncio
async def test_idor_prevented_on_integration_disconnect(client: AsyncClient):
    # Org 1 user attempts to trigger disconnect
    token1 = create_access_token(subject=1, role="Admin", organization_id=1)
    res = await client.post(
        "/api/integrations/kommo/disconnect",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "warning"
    assert "Nenhuma integração ativa encontrada" in data["message"]
