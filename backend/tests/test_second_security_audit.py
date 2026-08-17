import pytest
import pytest_asyncio
import jwt
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import (
    Base, User, Organization, OrganizationMember, Lead, Contact,
    Company, Pipeline, LeadStatus, Task, Event, CustomField, Tag, SyncLog
)
from app.integrations.kommo.models import CRMIntegration
from app.core.security import get_password_hash, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.database import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def audit_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        # 1. Setup Tenant A (Org 10)
        org_a = Organization(id=10, name="Empresa A", slug="org-a", is_active=True)
        # 2. Setup Tenant B (Org 20)
        org_b = Organization(id=20, name="Empresa B", slug="org-b", is_active=True)
        session.add_all([org_a, org_b])
        await session.flush()

        # Users for Org A
        admin_a = User(id=101, organization_id=10, name="Admin A", email="admin@a.com", hashed_password=get_password_hash("PassA123!"), role="Admin", is_active=True)
        consultora_a = User(id=102, organization_id=10, name="Consultora A", email="consultora@a.com", hashed_password=get_password_hash("PassA123!"), role="Consultora", is_active=True)
        
        # Users for Org B
        admin_b = User(id=201, organization_id=20, name="Admin B", email="admin@b.com", hashed_password=get_password_hash("PassB123!"), role="Admin", is_active=True)
        consultora_b = User(id=202, organization_id=20, name="Consultora B", email="consultora@b.com", hashed_password=get_password_hash("PassB123!"), role="Consultora", is_active=True)
        
        session.add_all([admin_a, consultora_a, admin_b, consultora_b])
        await session.flush()

        session.add(OrganizationMember(organization_id=10, user_id=101, role="Admin"))
        session.add(OrganizationMember(organization_id=10, user_id=102, role="Consultora"))
        session.add(OrganizationMember(organization_id=20, user_id=201, role="Admin"))
        session.add(OrganizationMember(organization_id=20, user_id=202, role="Consultora"))

        # Pipelines & Statuses
        pipe_a = Pipeline(id=11, organization_id=10, name="Funil A")
        pipe_b = Pipeline(id=21, organization_id=20, name="Funil B")
        session.add_all([pipe_a, pipe_b])
        await session.flush()

        status_a = LeadStatus(id=12, organization_id=10, pipeline_id=11, name="Fechado A", sort_order=1)
        status_b = LeadStatus(id=22, organization_id=20, pipeline_id=21, name="Fechado B", sort_order=1)
        session.add_all([status_a, status_b])
        await session.flush()

        # Data for Tenant A (100 leads, R$ 100.000)
        leads_a = [
            Lead(
                id=1000 + i,
                organization_id=10,
                external_id=10000 + i,
                name=f"Lead A {i}",
                price=1000.0,
                pipeline_id=11,
                status_id=12,
                responsible_user_id=102,
                unidade="Unidade Alpha",
                procedimento="Procedimento A",
                closed_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            for i in range(100)
        ]

        # Data for Tenant B (500 leads, R$ 500.000)
        leads_b = [
            Lead(
                id=2000 + i,
                organization_id=20,
                external_id=20000 + i,
                name=f"Lead B {i}",
                price=1000.0,
                pipeline_id=21,
                status_id=22,
                responsible_user_id=202,
                unidade="Unidade Beta",
                procedimento="Procedimento B",
                closed_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            for i in range(500)
        ]

        session.add_all(leads_a + leads_b)

        # Integration for Org B
        int_b = CRMIntegration(
            id="int_b_secret",
            organization_id=20,
            company_id="comp_b",
            provider="kommo",
            subdomain="kommo-b",
            client_id="cid_b",
            client_secret="csecret_b",
            access_token="token_b_private",
            refresh_token="refresh_b_private",
            status="connected"
        )
        session.add(int_b)
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def client(audit_session: AsyncSession):
    async def override_get_db():
        yield audit_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ==============================================================================
# 1. CROSS-TENANT ISOLATION MATRIX (A->A, B->B, A->B, B->A)
# ==============================================================================

@pytest.mark.asyncio
async def test_dashboard_strict_isolation_a_vs_b(client: AsyncClient):
    token_a = create_access_token(subject=101, role="Admin", organization_id=10)
    token_b = create_access_token(subject=201, role="Admin", organization_id=20)

    # A -> A : Exactly 100 leads, R$ 100.000
    res_a = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["total_sales"] == 100
    assert data_a["total_revenue"] == 100000.0

    # B -> B : Exactly 500 leads, R$ 500.000
    res_b = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["total_sales"] == 500
    assert data_b["total_revenue"] == 500000.0

    # A -> B : Attempting to access Tenant B via X-Organization-ID header
    res_a_to_b = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {token_a}", "X-Organization-ID": "20"})
    assert res_a_to_b.status_code == 403

    # B -> A : Attempting to access Tenant A via X-Organization-ID header
    res_b_to_a = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {token_b}", "X-Organization-ID": "10"})
    assert res_b_to_a.status_code == 403


# ==============================================================================
# 2. KOMMO CREDENTIALS & INTEGRATION ISOLATION
# ==============================================================================

@pytest.mark.asyncio
async def test_kommo_cross_tenant_forbidden(client: AsyncClient):
    token_a = create_access_token(subject=101, role="Admin", organization_id=10)
    token_b = create_access_token(subject=201, role="Admin", organization_id=20)

    # Org B has connected integration
    res_b_status = await client.get("/api/integrations/kommo/status", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b_status.status_code == 200
    assert res_b_status.json()["status"] == "connected"
    assert res_b_status.json()["id"] == "int_b_secret"

    # Org A checks status: must NOT see Org B's integration
    res_a_status = await client.get("/api/integrations/kommo/status", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a_status.status_code == 200
    assert res_a_status.json()["status"] == "disconnected"
    assert res_a_status.json()["id"] is None

    # Org A tries to disconnect Org B's integration
    res_a_dis = await client.post("/api/integrations/kommo/disconnect", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a_dis.status_code == 200
    assert res_a_dis.json()["status"] == "warning"


# ==============================================================================
# 3. JWT ADVERSARIAL EDGE CASES
# ==============================================================================

@pytest.mark.asyncio
async def test_jwt_expired_token(client: AsyncClient):
    expired_token = create_access_token(subject=101, role="Admin", organization_id=10, expires_delta=timedelta(seconds=-10))
    res = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_jwt_tampered_signature(client: AsyncClient):
    valid_token = create_access_token(subject=101, role="Admin", organization_id=10)
    tampered_token = valid_token[:-4] + "ABCD"
    res = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {tampered_token}"})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_jwt_none_algorithm_attack(client: AsyncClient):
    payload = {"sub": "101", "role": "Admin", "org_id": 10, "exp": datetime.now(timezone.utc) + timedelta(hours=1), "type": "access"}
    none_alg_token = jwt.encode(payload, key="", algorithm="none")
    res = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {none_alg_token}"})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_jwt_refresh_token_used_as_access_token(client: AsyncClient):
    refresh_token = create_refresh_token(subject=101, organization_id=10)
    # Sending refresh token to access-protected route
    res = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {refresh_token}"})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_jwt_access_token_used_as_refresh_token(client: AsyncClient):
    access_token = create_access_token(subject=101, role="Admin", organization_id=10)
    # Sending access token to refresh endpoint
    res = await client.post("/api/auth/refresh", json={"refresh_token": access_token})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_jwt_missing_subject(client: AsyncClient):
    payload = {"role": "Admin", "org_id": 10, "exp": datetime.now(timezone.utc) + timedelta(hours=1), "type": "access"}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    res = await client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


# ==============================================================================
# 4. MASS ASSIGNMENT & PRIVILEGE ESCALATION ATTEMPTS
# ==============================================================================

@pytest.mark.asyncio
async def test_login_mass_assignment_ignored(client: AsyncClient):
    # Attempt to inject elevated role or target org via login body
    res = await client.post("/api/auth/login", json={
        "email": "consultora@a.com",
        "password": "PassA123!",
        "role": "Owner",
        "organization_id": 20,
        "is_admin": True
    })
    assert res.status_code == 200
    data = res.json()
    # Must remain Consultora for Org 10
    assert data["role"] == "Consultora"
    assert data["organization"]["id"] == 10


# ==============================================================================
# 5. EXPORT & ALL DASHBOARD MODULES AUDIT
# ==============================================================================

@pytest.mark.asyncio
async def test_all_dashboard_routes_tenant_isolated(client: AsyncClient):
    token_a = create_access_token(subject=101, role="Admin", organization_id=10)

    routes = [
        "/api/dashboard/funnel",
        "/api/dashboard/revenue",
        "/api/dashboard/ranking",
        "/api/dashboard/losses",
        "/api/dashboard/origins",
        "/api/dashboard/tickets",
        "/api/dashboard/performance",
        "/api/dashboard/metrics",
        "/api/dashboard/options",
        "/api/dashboard/followup"
    ]

    for route in routes:
        res = await client.get(route, headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200, f"Failed on route {route}"
        # Ensure no leak of Org B data
        text_resp = res.text
        assert "Unidade Beta" not in text_resp
        assert "Procedimento B" not in text_resp
        assert "Funil B" not in text_resp

@pytest.mark.asyncio
async def test_html_export_tenant_isolated(client: AsyncClient):
    token_a = create_access_token(subject=101, role="Admin", organization_id=10)
    res = await client.get("/api/dashboard/export-html", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "dashboard_executivo_org-a.html" in res.headers["content-disposition"]
    # Verify content does not leak Org B data
    assert "Unidade Beta" not in res.text
    assert "Procedimento B" not in res.text
