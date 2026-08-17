import pytest
import pytest_asyncio
from datetime import timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import Base, User, Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token, decode_token
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
        # Seed test organization and users
        org = Organization(id=1, name="Clínica Alpha", slug="alpha", is_active=True)
        session.add(org)
        await session.flush()

        active_admin = User(
            id=1,
            organization_id=1,
            name="Admin User",
            email="admin@alpha.com",
            hashed_password=get_password_hash("Secret123!"),
            role="Admin",
            is_active=True
        )
        inactive_user = User(
            id=2,
            organization_id=1,
            name="Inactive User",
            email="inactive@alpha.com",
            hashed_password=get_password_hash("Secret123!"),
            role="Consultora",
            is_active=False
        )
        session.add_all([active_admin, inactive_user])
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
async def test_login_success(client: AsyncClient):
    res = await client.post("/api/auth/login", json={
        "email": "admin@alpha.com",
        "password": "Secret123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "Admin"
    assert data["organization"]["slug"] == "alpha"

    # Verify claims
    claims = decode_token(data["access_token"])
    assert claims["sub"] == "1"
    assert claims["role"] == "Admin"
    assert claims["org_id"] == 1

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    res = await client.post("/api/auth/login", json={
        "email": "admin@alpha.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401
    assert "Credenciais inválidas" in res.json()["detail"]

@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    res = await client.post("/api/auth/login", json={
        "email": "ghost@alpha.com",
        "password": "Secret123!"
    })
    assert res.status_code == 401
    assert "Credenciais inválidas" in res.json()["detail"]

@pytest.mark.asyncio
async def test_login_inactive_user_blocked(client: AsyncClient):
    res = await client.post("/api/auth/login", json={
        "email": "inactive@alpha.com",
        "password": "Secret123!"
    })
    assert res.status_code == 403
    assert "inativa" in res.json()["detail"]

@pytest.mark.asyncio
async def test_token_refresh_flow(client: AsyncClient):
    # 1. Login
    login_res = await client.post("/api/auth/login", json={
        "email": "admin@alpha.com",
        "password": "Secret123!"
    })
    refresh_token = login_res.json()["refresh_token"]

    # 2. Refresh
    refresh_res = await client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["user_id"] == 1

@pytest.mark.asyncio
async def test_invalid_refresh_token(client: AsyncClient):
    res = await client.post("/api/auth/refresh", json={
        "refresh_token": "invalid.jwt.token"
    })
    assert res.status_code == 401
