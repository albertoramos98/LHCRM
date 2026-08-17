# Arquitetura do Sistema — LHCRM Pro

## 1. Visão Geral da Arquitetura

O **LHCRM Pro** é uma plataforma SaaS multi-tenant de alto desempenho para gestão executiva de CRM, métricas de funil, produtividade comercial e inteligência de vendas.

O sistema é construído sobre uma arquitetura desacoplada em camadas (**Layered Architecture**) orientada a serviços e repositórios assíncronos.

```
┌──────────────────────────────────────────────────────────────┐
│                  Frontend (React + Vite)                     │
│    - TypeScript, TailwindCSS, Recharts, Lucide Icons         │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTPS / JSON REST API
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI Async)                    │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Security & Middlewares: CORS, RateLimit, SecurityHeaders │ │
│ ├──────────────────────────────────────────────────────────┤ │
│ │ Dependency Injection: Auth, TenantContext, RBAC          │ │
│ ├──────────────────────────────────────────────────────────┤ │
│ │ Routes / Controllers: Auth, Dashboard, Sync, Kommo OAuth │ │
│ ├──────────────────────────────────────────────────────────┤ │
│ │ Domain Services: KommoSyncService, DashboardService       │ │
│ ├──────────────────────────────────────────────────────────┤ │
│ │ Repositories: SyncRepository, DashboardRepository        │ │
│ └────────────────────────────┬─────────────────────────────┘ │
└──────────────────────────────┼───────────────────────────────┘
                               │ SQLAlchemy Async (AsyncPG / aiosqlite)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│           PostgreSQL Database (Supabase Pooler / Local)      │
│       - Multi-Tenant Schema, Composite Unique Indexes        │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Camadas do Backend

### 2.1. Camada de Apresentação (Routes / Controllers)
- **`app/routes/auth.py`**: Login, renovação de tokens JWT (access + refresh), consulta ao usuário ativo (`/me`).
- **`app/routes/dashboard.py`**: Endpoints de agregação analítica (receita, ticket médio, funil, perdas, ranking, atendimento, follow-up, origens).
- **`app/routes/sync.py`**: Disparo de sincronização manual e consulta ao status da última sincronização.
- **`app/integrations/kommo/routes.py`**: Fluxo OAuth 2.0 com o Kommo CRM (connect, callback, disconnect, refresh-token, sync).

### 2.2. Camada de Segurança e Injeção de Dependências
- **`app/core/security.py`**: Criação de tokens JWT assinados com algoritmo HS256, hash de senhas via passlib/bcrypt, validação de tokens.
- **`app/core/dependencies.py`**:
  - `get_current_user`: Extrai e valida o token Bearer e localiza o usuário no banco de dados.
  - `get_current_active_user`: Garante que o usuário não está desativado (`is_active=True`).
  - `get_tenant_context`: Resolve e valida o tenant ativo do usuário, prevenindo acesso cruzado.
  - `require_role(roles)` e `require_admin`: Controle de acesso baseado em papéis (RBAC).
  - `rate_limit_login` e `rate_limit_sync`: Prevenção contra abuso e força bruta.

### 2.3. Camada de Serviços de Negócio (Domain Services)
- **`app/services/dashboard_service.py`**: Regras de negócio, cálculos agregados e cache em memória isolado por tenant (`org:{id}:{prefix}:{params}`).
- **`app/services/sync_service.py`**: Orquestrador de sincronização dos dados do CRM para as tabelas locais.
- **`app/services/html_generator.py`**: Renderização do relatório HTML executivo independente com dados do tenant embutidos.

### 2.4. Camada de Acesso a Dados (Repositories)
- **`app/repositories/dashboard_repository.py`**: Consultas analíticas SQL assíncronas com garantia de filtragem por `organization_id`.
- **`app/repositories/sync_repository.py`**: Upserts idempotentes com chaves compostas `(organization_id, external_id)`.

---

## 3. Ciclo de Vida da Requisição

1. **Recepção**: O cliente envia a requisição HTTP contendo o cabeçalho `Authorization: Bearer <token>` e opcionalmente `X-Organization-ID`.
2. **Middleware**:
   - `SecurityHeadersMiddleware` injeta headers de proteção.
   - `CORSMiddleware` valida a origem permitida.
3. **Autenticação & Tenancy**:
   - `get_tenant_context` decodifica o JWT, valida a expiração, localiza o usuário e valida o vínculo à organização alvo.
4. **Autorização (RBAC)**:
   - `require_role` valida se a função do usuário (`Owner`, `Admin`, `Gerente`, `Consultora`) possui privilégios para a ação.
5. **Execução do Serviço & Repositório**:
   - O repositório executa a query no PostgreSQL limitando estritamente os registros a `organization_id == tenant.organization_id`.
6. **Resposta Sanitizada**:
   - O schema Pydantic filtra e valida o retorno antes do envio ao cliente.
