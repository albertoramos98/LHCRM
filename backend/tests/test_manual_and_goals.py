import pytest
import pytest_asyncio
import io
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.domain import Base, User, Organization, OrganizationMember, Lead, Pipeline, LeadStatus, MacroMetric
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
        # Organization A
        org_a = Organization(id=1, name="Clínica Alpha", slug="alpha", is_active=True)
        # Organization B
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

        # Pipeline & Status for Org A
        pipe_a = Pipeline(id=1, organization_id=1, name="Funil Alpha")
        session.add(pipe_a)
        await session.flush()

        status_a = LeadStatus(id=1, organization_id=1, pipeline_id=1, name="Ganhos", type=2)
        session.add(status_a)
        await session.flush()

        # Pipeline & Status for Org B
        pipe_b = Pipeline(id=2, organization_id=2, name="Funil Beta")
        session.add(pipe_b)
        await session.flush()

        status_b = LeadStatus(id=2, organization_id=2, pipeline_id=2, name="Ganhos B", type=2)
        session.add(status_b)
        await session.flush()

        # Initial Lead in Org A
        lead_kommo = Lead(
            id=1, organization_id=1, external_id=999, source_type="kommo",
            name="Lead Kommo Auto", price=15000.0, pipeline_id=1, status_id=1,
            closed_at=datetime.now(timezone.utc), unidade="Matriz"
        )
        session.add(lead_kommo)
        await session.commit()

        yield session

@pytest.mark.asyncio
async def test_manual_lead_creation_and_listing(test_db_session):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    token_a = create_access_token(subject=1, role="Admin", organization_id=1)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a manual lead
        payload = {
            "name": "Paciente VIP Manual",
            "price": 25000.0,
            "pipeline_id": 1,
            "status_id": 1,
            "unidade": "Matriz",
            "procedimento": "Implante",
            "origem": "Indicação",
            "source_type": "manual"
        }
        res = await client.post("/api/leads", json=payload, headers=headers_a)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Paciente VIP Manual"
        assert data["price"] == 25000.0
        assert data["source_type"] == "manual"
        lead_id = data["id"]

        # 2. List leads with source_type filter
        res_list = await client.get("/api/leads?source_type=manual", headers=headers_a)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert list_data["total"] == 1
        assert list_data["items"][0]["name"] == "Paciente VIP Manual"

        # 3. Update the lead price
        res_update = await client.put(f"/api/leads/{lead_id}", json={"price": 28000.0}, headers=headers_a)
        assert res_update.status_code == 200
        assert res_update.json()["price"] == 28000.0

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_dashboard_source_filtering(test_db_session):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    token_a = create_access_token(subject=1, role="Admin", organization_id=1)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a manual lead
        await client.post("/api/leads", json={
            "name": "Lead Manual Test",
            "price": 5000.0,
            "pipeline_id": 1,
            "status_id": 1,
            "source_type": "manual"
        }, headers=headers_a)

        # Overview with all (should have kommo 15000 + manual 5000 = 20000)
        res_all = await client.get("/api/dashboard/overview?source_type=all", headers=headers_a)
        assert res_all.status_code == 200
        assert res_all.json()["total_revenue"] == 20000.0

        # Overview with kommo only (should be 15000)
        res_kommo = await client.get("/api/dashboard/overview?source_type=kommo", headers=headers_a)
        assert res_kommo.status_code == 200
        assert res_kommo.json()["total_revenue"] == 15000.0

        # Overview with manual only (should be 5000)
        res_manual = await client.get("/api/dashboard/overview?source_type=manual", headers=headers_a)
        assert res_manual.status_code == 200
        assert res_manual.json()["total_revenue"] == 5000.0

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_csv_import_leads(test_db_session):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    token_a = create_access_token(subject=1, role="Admin", organization_id=1)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    csv_content = """Nome;Valor;Unidade;Procedimento;Origem
João Silva;12000,00;Matriz;Harmonização;Instagram
Maria Santos;8500,50;Filial;Ortodontia;Google Ads
"""
    files = {"file": ("leads.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/leads/import-csv", files=files, headers=headers_a)
        assert res.status_code == 200
        summary = res.json()
        assert summary["total_rows"] == 2
        assert summary["imported_count"] == 2
        assert summary["failed_count"] == 0

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_goals_and_cac_metrics(test_db_session):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    token_a = create_access_token(subject=1, role="Admin", organization_id=1)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        now = datetime.now(timezone.utc)
        current_month = f"{now.year:04d}-{now.month:02d}"

        # 1. Create monthly goal with marketing investment
        goal_payload = {
            "period_month": current_month,
            "revenue_target": 100000.0,
            "leads_target": 50,
            "sales_target": 10,
            "marketing_investment": 3000.0,
            "notes": "Meta Q3"
        }
        res = await client.post("/api/goals", json=goal_payload, headers=headers_a)
        assert res.status_code == 200
        assert res.json()["revenue_target"] == 100000.0

        # 2. Get Goal summary with CAC & ROI calculation
        res_sum = await client.get(f"/api/goals/summary?period_month={current_month}", headers=headers_a)
        assert res_sum.status_code == 200
        sum_data = res_sum.json()
        assert sum_data["revenue_target"] == 100000.0
        assert sum_data["marketing_investment"] == 3000.0
        assert sum_data["cac"] > 0
        assert sum_data["roi"] > 0

    app.dependency_overrides.clear()
