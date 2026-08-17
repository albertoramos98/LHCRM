import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import Base, User, Organization, OrganizationMember
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
        org = Organization(id=1, name="Clínica Beta", slug="beta", is_active=True)
        session.add(org)
        await session.flush()

        admin_user = User(
            id=1,
            organization_id=1,
            name="Admin Beta",
            email="admin@beta.com",
            hashed_password=get_password_hash("Pass123!"),
            role="Admin",
            is_active=True
        )
        consultora_user = User(
            id=2,
            organization_id=1,
            name="Consultora Beta",
            email="consultora@beta.com",
            hashed_password=get_password_hash("Pass123!"),
            role="Consultora",
            is_active=True
        )
        session.add_all([admin_user, consultora_user])
        await session.flush()

        session.add(OrganizationMember(organization_id=1, user_id=1, role="Admin"))
        session.add(OrganizationMember(organization_id=1, user_id=2, role="Consultora"))
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
async def test_unauthenticated_access_rejected(client: AsyncClient):
    res = await client.get("/api/dashboard/overview")
    assert res.status_code == 401
    assert "Autenticação necessária" in res.json()["detail"]

@pytest.mark.asyncio
async def test_authenticated_dashboard_access(client: AsyncClient):
    token = create_access_token(subject=1, role="Admin", organization_id=1)
    res = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_consultora_forbidden_from_admin_actions(client: AsyncClient):
    # Consultora token
    consultora_token = create_access_token(subject=2, role="Consultora", organization_id=1)
    
    # Try connecting Kommo (Admin only)
    res = await client.post(
        "/api/integrations/kommo/connect",
        json={"subdomain": "minhaempresa"},
        headers={"Authorization": f"Bearer {consultora_token}"}
    )
    assert res.status_code == 403
    assert "Permissão insuficiente" in res.json()["detail"]

@pytest.mark.asyncio
async def test_admin_allowed_for_integration_connect(client: AsyncClient):
    admin_token = create_access_token(subject=1, role="Admin", organization_id=1)
    res = await client.post(
        "/api/integrations/kommo/connect",
        json={"subdomain": "empresa-beta"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert "auth_url" in res.json()
