"""
Script CLI para Validacao e Teste de Integracao com o Kommo CRM.
Executa verificacoes de conexao, sincronizacao de pipelines, leads, status e tarefas.
Uso:
    python test_kommo_cli.py
"""
import asyncio
import sys
import io
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.models.domain import Base, Organization, Pipeline, LeadStatus, Lead, Task
from app.integrations.kommo.models import CRMIntegration, IntegrationLog
from app.integrations.kommo.oauth import KommoOAuthService
from app.integrations.kommo.sync import KommoIntegrationSyncService

# Set utf-8 stdout if needed
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=" * 60)
    print(" [*] LHCRM - Teste de Integracao Kommo CRM")
    print("=" * 60)

    db_url = settings.DATABASE_URL
    print(f"[*] Conectando ao Banco de Dados ({db_url.split('@')[-1] if '@' in db_url else 'local'})...")

    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Check Organization
        from sqlalchemy import select
        res = await session.execute(select(Organization).limit(1))
        org = res.scalar_one_or_none()
        if not org:
            print("[+] Criando Organizacao padrao de teste (LHCRM Master)...")
            org = Organization(id=1, name="LHCRM Master", slug="master", is_active=True)
            session.add(org)
            await session.commit()

        print(f"[OK] Organizacao Ativa: ID {org.id} ({org.name})")

        # Test OAuth Flow
        oauth_service = KommoOAuthService(session, organization_id=org.id)
        print("[*] Testando Normalizacao de Dominio...")
        subdomain = oauth_service.normalize_subdomain("demo.kommo.com")
        print(f"[OK] Subdominio normalizado: {subdomain}")

        print("[*] Simulando Conexao OAuth com Kommo...")
        integration = await oauth_service.exchange_code(
            code="demo_cli_test_token",
            raw_subdomain="demo.kommo.com",
            company_id=f"comp_{org.id}"
        )
        print(f"[OK] Integracao Ativa: ID {integration.id} | Status: {integration.status.upper()}")

        # Test Token Retrieval
        print("[*] Validando Token de Acesso...")
        valid_token = await oauth_service.get_valid_token(integration.id)
        print(f"[OK] Token Ativo e Valido: {valid_token[:15]}... (OK)")

        # Test Sync
        print("[*] Executando Sincronizacao Completa de Entidades (Pipelines, Leads, Status)...")
        sync_service = KommoIntegrationSyncService(session, organization_id=org.id)
        sync_result = await sync_service.sync_integration(integration.id, trigger_type="manual_cli")

        print(f"[OK] Sincronizacao Concluida com Sucesso!")
        print(f"    - Registros sincronizados: {sync_result['items_synced']}")
        print(f"    - Timestamp: {sync_result['last_sync']}")

        # Fetch and display Stats
        stats = await sync_service.get_integration_status_and_stats(company_id=integration.company_id)
        print("\n" + "-" * 40)
        print(" Estatisticas Consolidadas do Kommo")
        print("-" * 40)
        for entity, count in stats["entity_counts"].items():
            print(f"   * {entity.capitalize():<12}: {count:>4} registros")
        print("-" * 40)
        print(" [OK] Todos os testes de integracao do Kommo passaram com sucesso!")
        print("=" * 60 + "\n")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
