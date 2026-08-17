import pytest
import pytest_asyncio
import base64
import json
import hmac
import hashlib
import time
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import Base, User, Organization, OrganizationMember
from app.integrations.kommo.oauth import KommoOAuthService
from app.core.security import get_password_hash, create_access_token
from app.core.config import settings
from app.core.database import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def hardening_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        # Active Org
        active_org = Organization(id=50, name="Org Ativa", slug="ativa", is_active=True)
        # Inactive Org
        inactive_org = Organization(id=51, name="Org Inativa", slug="inativa", is_active=False)
        session.add_all([active_org, inactive_org])
        await session.flush()

        # Valid user with active org
        valid_user = User(
            id=501, organization_id=50, name="Valid User",
            email="valid@ativa.com", hashed_password=get_password_hash("Pass123!"),
            role="Admin", is_active=True
        )
        # Orphan user with no organization_id and no membership
        orphan_user = User(
            id=502, organization_id=None, name="Orphan User",
            email="orphan@nowhere.com", hashed_password=get_password_hash("Pass123!"),
            role="Consultora", is_active=True
        )
        # User in inactive org
        inactive_org_user = User(
            id=503, organization_id=51, name="Inactive Org User",
            email="user@inativa.com", hashed_password=get_password_hash("Pass123!"),
            role="Admin", is_active=True
        )
        session.add_all([valid_user, orphan_user, inactive_org_user])
        await session.flush()

        session.add(OrganizationMember(organization_id=50, user_id=501, role="Admin"))
        session.add(OrganizationMember(organization_id=51, user_id=503, role="Admin"))
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def client(hardening_session: AsyncSession):
    async def override_get_db():
        yield hardening_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ==============================================================================
# 1. ORPHAN USER TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_orphan_user_rejected(client: AsyncClient):
    # 1. Orphan user (organization_id = None) -> MUST receive 403 Forbidden
    orphan_token = create_access_token(subject=502, role="Consultora", organization_id=None)
    res_orphan = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {orphan_token}"})
    assert res_orphan.status_code == 403
    assert "Usuário não associado a nenhuma organização válida" in res_orphan.json()["detail"]

    # 2. Valid user with active org -> MUST succeed
    valid_token = create_access_token(subject=501, role="Admin", organization_id=50)
    res_valid = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {valid_token}"})
    assert res_valid.status_code == 200

    # 3. Valid user trying to access a non-existent org -> MUST receive 403 Forbidden
    res_non_existent = await client.get(
        "/api/dashboard/overview",
        headers={"Authorization": f"Bearer {valid_token}", "X-Organization-ID": "9999"}
    )
    assert res_non_existent.status_code == 403

    # 4. User associated with an inactive org -> MUST receive 403 Forbidden
    inactive_token = create_access_token(subject=503, role="Admin", organization_id=51)
    res_inactive = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {inactive_token}"})
    assert res_inactive.status_code == 403
    assert "inativa" in res_inactive.json()["detail"].lower()


# ==============================================================================
# 2. HMAC OAUTH STATE PROTECTION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_hmac_oauth_state_valid(hardening_session: AsyncSession):
    oauth_service = KommoOAuthService(hardening_session, organization_id=50)
    state = oauth_service.create_oauth_state()
    
    # Valid state
    payload = KommoOAuthService.verify_oauth_state(state)
    assert payload["org_id"] == 50
    assert "nonce" in payload
    assert payload["exp"] > time.time()

@pytest.mark.asyncio
async def test_hmac_oauth_state_tampered(hardening_session: AsyncSession):
    oauth_service = KommoOAuthService(hardening_session, organization_id=50)
    state = oauth_service.create_oauth_state()
    
    raw_b64, signature = state.split(".")
    # Tamper with signature
    tampered_sig = signature[:-4] + "dead"
    tampered_state = f"{raw_b64}.{tampered_sig}"
    
    with pytest.raises(ValueError, match="Assinatura criptográfica do state OAuth inválida"):
        KommoOAuthService.verify_oauth_state(tampered_state)

@pytest.mark.asyncio
async def test_hmac_oauth_state_expired(hardening_session: AsyncSession):
    payload = {
        "org_id": 50,
        "company_id": "org_50",
        "nonce": "testnonce123",
        "exp": int(time.time()) - 100 # expired
    }
    raw_json = json.dumps(payload, sort_keys=True)
    raw_b64 = base64.urlsafe_b64encode(raw_json.encode()).decode()
    signature = hmac.new(settings.SECRET_KEY.encode(), raw_b64.encode(), hashlib.sha256).hexdigest()
    expired_state = f"{raw_b64}.{signature}"

    with pytest.raises(ValueError, match="O token de state OAuth expirou"):
        KommoOAuthService.verify_oauth_state(expired_state)

@pytest.mark.asyncio
async def test_hmac_oauth_state_altered_org_id(hardening_session: AsyncSession):
    oauth_service = KommoOAuthService(hardening_session, organization_id=50)
    state = oauth_service.create_oauth_state()
    
    raw_b64, signature = state.split(".")
    # Decode and tamper payload
    payload = json.loads(base64.urlsafe_b64decode(raw_b64.encode()).decode())
    payload["org_id"] = 99 # changed org_id
    tampered_raw_b64 = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True).encode()).decode()
    tampered_state = f"{tampered_raw_b64}.{signature}"

    with pytest.raises(ValueError, match="Assinatura criptográfica do state OAuth inválida"):
        KommoOAuthService.verify_oauth_state(tampered_state)


# ==============================================================================
# 3. HTTPONLY COOKIE & AUTH FLOW
# ==============================================================================

@pytest.mark.asyncio
async def test_httponly_cookie_login_and_refresh(client: AsyncClient):
    # 1. Login
    login_res = await client.post("/api/auth/login", json={
        "email": "valid@ativa.com",
        "password": "Pass123!"
    })
    assert login_res.status_code == 200
    assert "lhcrm_refresh_token" in login_res.cookies

    # 2. Refresh without body (using HttpOnly cookie)
    refresh_res = await client.post("/api/auth/refresh")
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()

    # 3. Logout clears cookie
    logout_res = await client.post("/api/auth/logout")
    assert logout_res.status_code == 200
    # Cookie should be expired/deleted
    assert logout_res.cookies.get("lhcrm_refresh_token") is None or logout_res.headers.get("set-cookie")


# ==============================================================================
# 4. CSP AND SECURITY HEADERS
# ==============================================================================

@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    res = await client.get("/")
    assert res.status_code == 200
    headers = res.headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "SAMEORIGIN"
    assert headers["x-xss-protection"] == "1; mode=block"
    assert "content-security-policy" in headers
    assert "default-src 'self'" in headers["content-security-policy"]
