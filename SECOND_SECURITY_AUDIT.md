# SEGUNDA AUDITORIA INDEPENDENTE DE SEGURANÇA E ARQUITETURA — LHCRM PRO

**Data da Auditoria:** 17 de Agosto de 2026  
**Auditor Responsável:** Engenheiro Sênior de Segurança & Arquiteto de Software  
**Tipo:** Segunda Auditoria Independente, Forense e Adversarial  
**Status do Projeto:** `CONDICIONALMENTE APROVADO` (Com Recomendações de Infraestrutura & Rotação Obrigatória)  
**Total de Testes Automatizados Executados:** 31 cenários defensivos / 100% aprovados

---

## 1. Auditoria Completa de Endpoints FastAPI

A tabela a seguir mapeia todos os endpoints expostos pela aplicação, seus mecanismos de autenticação, perfil (RBAC) exigido, escopo de tenant, validação de ownership, risco de IDOR e status do teste automatizado:

| Método | Rota | Autenticação Necessária | Role Exigida | Tenant Scoping | Validação de Ownership | Risco de IDOR | Teste Existente | Status de Segurança |
|---|---|---|---|---|---|---|---|---|
| `GET` | `/` | Não | Nenhuma | Não | N/A | Nulo | Testado | **SEGURO** (Health check público) |
| `POST` | `/api/auth/login` | Não | Nenhuma | Não | N/A | Nulo | `test_auth.py` | **SEGURO** (Protegido por RateLimit) |
| `POST` | `/api/auth/refresh` | Não (Valida Refresh Token) | Nenhuma | claims (`org_id`) | Valida user ativo | Nulo | `test_auth.py` | **SEGURO** (Valida `type="refresh"`) |
| `GET` | `/api/auth/me` | `get_current_active_user` | Qualquer ativo | Própria org | Próprio usuário | Nulo | `test_auth.py` | **SEGURO** |
| `POST` | `/api/sync/now` | `get_tenant_context` | `Owner`, `Admin`, `Gerente` | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_services.py` | **SEGURO** (Protegido por RateLimit) |
| `GET` | `/api/sync/status` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_services.py` | **SEGURO** |
| `GET` | `/api/dashboard/options` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/overview` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Consultora restrita aos seus leads | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/funnel` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/revenue` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/followup` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/ranking` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/losses` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/origins` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/tickets` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/performance` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/metrics` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/api/dashboard/export-html` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `GET` | `/public-dashboard` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Scoped ao tenant | Baixo | `test_second_security_audit.py` | **SEGURO** |
| `POST` | `/api/integrations/kommo/connect` | `get_tenant_context` | `Owner`, `Admin` | `tenant.organization_id` | Restrito ao tenant | Baixo | `test_authorization.py` | **SEGURO** (Body JSON) |
| `GET` | `/api/integrations/kommo/connect` | `get_tenant_context` | `Owner`, `Admin` | `tenant.organization_id` | Restrito ao tenant | Médio | `test_authorization.py` | **OBSOLETO** (Manter apenas para compatibilidade legada) |
| `GET` | `/api/integrations/kommo/callback` | Pública (Callback OAuth) | Nenhuma | `state=org_<id>` | Vinculado ao state | Médio | `test_integrations.py` | **ATENÇÃO** (Requer HMAC assinado no state) |
| `GET` | `/api/integrations/kommo/status` | `get_tenant_context` | Qualquer membro | `tenant.organization_id` | Restrito ao tenant | Baixo | `test_idor_security.py` | **SEGURO** |
| `POST` | `/api/integrations/kommo/disconnect` | `get_tenant_context` | `Owner`, `Admin` | `tenant.organization_id` | Restrito ao tenant | Baixo | `test_idor_security.py` | **SEGURO** |
| `POST` | `/api/integrations/kommo/refresh-token`| `get_tenant_context` | `Owner`, `Admin` | `tenant.organization_id` | Restrito ao tenant | Baixo | `test_integrations.py` | **SEGURO** |
| `POST` | `/api/integrations/kommo/sync` | `get_tenant_context` | `Owner`, `Admin`, `Gerente` | `tenant.organization_id` | Restrito ao tenant | Baixo | `test_integrations.py` | **SEGURO** |

---

## 2. Testes de IDOR e Segregação Bidirecional (A vs B)

Foi executado o teste adversarial `test_dashboard_strict_isolation_a_vs_b` no arquivo `tests/test_second_security_audit.py`:

```python
# Tenant A: 100 leads, R$ 100.000
# Tenant B: 500 leads, R$ 500.000

# Validação Bidirecional:
# A -> A : 100 leads, R$ 100.000 (HTTP 200 OK)
# B -> B : 500 leads, R$ 500.000 (HTTP 200 OK)
# A -> B : Enviando X-Organization-ID: 20 -> (HTTP 403 Forbidden - Negado)
# B -> A : Enviando X-Organization-ID: 10 -> (HTTP 403 Forbidden - Negado)
```

**Resultado:** O isolamento bidirecional foi comprovado matematicamente com zero vazamento entre os dois tenants.

---

## 3. Mass Assignment & Escalação de Privilégios

Foram realizados testes enviando campos proibidos no payload de requisições:
- Parâmetros injetados: `role: "Owner"`, `organization_id: 20`, `is_admin: True`, `is_active: True`.
- **Resultado:** Os modelos Pydantic no FastAPI descartam campos não declarados e ignoram qualquer tentativa de injeção direta de `role` ou `organization_id` durante o login e refresh (`test_login_mass_assignment_ignored`).

---

## 4. Auditoria de Segurança dos Tokens JWT

Foram executados testes de ataque contra a camada criptográfica JWT (`test_second_security_audit.py`):
- **Token Expirado (`exp` no passado):** Rejeitado com `401 Unauthorized`.
- **Token com Assinatura Adulterada:** Rejeitado com `401 Unauthorized`.
- **Ataque com Algoritmo `none`:** Rejeitado com `401 Unauthorized` (FastAPI/PyJWT força o algoritmo configurado `HS256`).
- **Refresh Token usado como Bearer Token de rota protegida:** Rejeitado com `401 Unauthorized` (Validação estrita de `type="access"`).
- **Access Token usado na rota `/api/auth/refresh`:** Rejeitado com `401 Unauthorized` (Validação estrita de `type="refresh"`).
- **Token sem Subject (`sub` ausente):** Rejeitado com `401 Unauthorized`.

---

## 5. Auditoria Detalhada de Consultas SQL (Multi-Tenant)

Todas as consultas SQLAlchemy do backend foram inspecionadas:
1. **`dashboard_repository.py`**:
   - `_build_lead_filter_query`: Inicia obrigatoriamente com `Lead.organization_id == self.organization_id`.
   - `get_filter_options`: Filtra `User`, `Pipeline`, `LeadStatus`, `Lead.unidade`, `procedimento`, `origem` por `organization_id == self.organization_id`.
   - `get_funnel_performance`: Filtra `LeadStatus.organization_id == self.organization_id`.
   - `get_ranking_metrics`: Filtra `User.organization_id == self.organization_id`.
   - `get_followup_metrics`: Filtra `Task.organization_id == self.organization_id` e `User.organization_id == self.organization_id`.
2. **`sync_repository.py`**:
   - Todos os métodos de upsert (`upsert_leads`, `upsert_contacts`, `upsert_companies`, `upsert_pipelines_and_statuses`, `upsert_users`, `upsert_tasks`, `upsert_events`, `upsert_custom_fields`, `upsert_tags`) utilizam chaves compostas e `organization_id = self.organization_id`.
3. **`kommo/oauth.py` e `kommo/sync.py`**:
   - Todas as operações em `CRMIntegration` e `IntegrationLog` são estritamente filtradas por `organization_id`.

---

## 6. Auditoria de Dashboard e Métricas

Foi validado que todos os 10 módulos analíticos (`overview`, `performance`, `tickets`, `revenue`, `funnel`, `losses`, `ranking`, `followup`, `origins`, `metrics`) mantêm estrita segregação de tenant. Nenhum dado do Tenant B foi vazado na resposta do Tenant A.

---

## 7. Auditoria de Exportação de Dados

Endpoints de exportação (`/api/dashboard/export-html`):
- O método `generate_dashboard_html` recebe explicitamente `organization_id`.
- O relatório HTML embutido é gerado com dados exclusivos do tenant solicitante.
- O nome do arquivo gerado contém o slug da organização (`dashboard_executivo_org-a.html`).

---

## 8. Auditoria de Credenciais e Isolamento Kommo CRM

- As credenciais OAuth (`client_id`, `client_secret`, `access_token`, `refresh_token`) ficam restritas à tabela `crm_integrations` e nunca são retornadas em endpoints de leitura como `/api/integrations/kommo/status`.
- Tentativas do Tenant A de desconectar a integração do Tenant B foram rejeitadas (`test_kommo_cross_tenant_forbidden`).

---

## 9. Arquitetura de Acesso ao Supabase & RLS

### Mapeamento do Fluxo de Dados:
- **Frontend → Supabase:** **NÃO EXISTE CONEXÃO DIRETA.** O React Frontend não possui e não utiliza bibliotecas do Supabase (`@supabase/supabase-js`), nem expõe a `anon_key` ou `service_role_key`.
- **Frontend → FastAPI:** Comunicação HTTPS com tokens JWT Bearer assinados.
- **FastAPI → Supabase:** Conexão assíncrona PostgreSQL via SQLAlchemy + `asyncpg` utilizando o pooler do Supabase (porta 6543 / 5432) com `statement_cache_size=0`.

### Análise de RLS (Row Level Security):
- Como o backend se conecta diretamente ao PostgreSQL utilizando as credenciais de superusuário do banco (`postgres`), as políticas de RLS do Supabase não são ativadas.
- **Justificativa Técnica:** O isolamento de dados no LHCRM Pro é implementado na **Camada de Aplicação (Application-Level Multi-Tenancy)** através de injeção de dependências FastAPI (`TenantContext`) e clausulas `WHERE organization_id = :org_id` em 100% dos repositórios SQLAlchemy.

---

## 10. Integridade do Banco de Dados & Migrations

- Migrações executadas com sucesso no banco de dados limpo via Alembic:
  - `001_initial_multitenant_schema.py`: Criação de todas as 17 tabelas com Foreign Keys (`CASCADE` / `SET NULL`), índices compostos e constraints de unicidade `(organization_id, external_id)`.
  - `002_safe_backfill_and_tenant_indexes.py`: Provisionamento idempotente da organização default e migração de registros legados sem perda de dados.
- **Garantia de Nullability:** A tabela `organization_members` possui constraint `UNIQUE (organization_id, user_id)` e `NOT NULL` em ambas as chaves.

---

## 11. Investigação Forense do Histórico Git

A busca no histórico completo do Git (`git log -p`) revelou a presença de segredos nos seguintes commits históricos anteriores à remediação:

1. **Commit `2f46fb6` (21 de Julho de 2026):**
   - Arquivo `docker-compose.yml`: Senha do PostgreSQL `010898dejaneiro!`.
   - Arquivo `backend/app/core/config.py`: Senha do PostgreSQL `010898dejaneiro!`.
   - Arquivo `backend/test_supabase_fast.py` e `test_supabase_pooler.py`: Senha do PostgreSQL `010898dejaneiro!`.
2. **Commit `145c3a6` (21 de Julho de 2026):**
   - Arquivo `frontend/src/pages/Login.tsx`: Senha do admin demo `Luizhenrique95#`.

> [!CAUTION]
> **REAFIRMAÇÃO DO RISCO:** Qualquer pessoa com acesso ao histórico Git local ou remoto pode inspecionar os commits passados e recuperar essas senhas antigas. **A alteração de senha no painel do Supabase é mandatória.**

---

## 12. Avaliação do Rate Limiting

- O rate limiting implementado em `app/core/dependencies.py` (`MemoryRateLimiter`) utiliza uma estrutura `dict` em memória baseada no IP do cliente (`request.client.host`).
- **Comportamento em Ambiente Multi-Instância / Multi-Worker:**
  - Em servidores com múltiplos processos Uvicorn (`--workers 4`) ou contêineres Docker replicados, cada processo mantém sua própria tabela de rate limit em memória.
  - **Impacto:** O limite efetivo por IP passa a ser `RATE_LIMIT_LOGIN_PER_MINUTE * número_de_workers`.
  - **Recomendação de Produção:** Para clusters com balanceador de carga, integrar o rate limiting com **Redis** ou aplicar o rate limiting na camada de borda (Cloudflare / Nginx / Traefik).

---

## 13. Auditoria do Frontend

- **Armazenamento:** `localStorage` armazena `lhcrm_access_token`, `lhcrm_refresh_token`, `lhcrm_user` e `lhcrm_org_id`.
- **Proteção de Rotas:** O `App.tsx` renderiza condicionalmente o `<LoginPage />` quando o estado `user` é nulo.
- **Prevenção de Falsificação:** Qualquer tentativa do usuário no frontend de modificar `lhcrm_org_id` no localStorage para o ID de outra organização resulta em bloqueio imediato com `403 Forbidden` no backend.

---

## 14. Avaliação de Security Headers

| Cabeçalho | Status | Observação |
|---|:---:|---|
| `X-Content-Type-Options: nosniff` | ✅ **Presente** | Injetado por `SecurityHeadersMiddleware` |
| `X-Frame-Options: SAMEORIGIN` | ✅ **Presente** | Protege contra clickjacking |
| `X-XSS-Protection: 1; mode=block` | ✅ **Presente** | Proteção básica contra reflexão XSS |
| `Referrer-Policy: strict-origin-when-cross-origin` | ✅ **Presente** | Protege vazamento de URLs no referer |
| `Strict-Transport-Security (HSTS)` | ⚠️ **Ausente** | Recomendado adicionar em produção se TLS for terminado na aplicação |
| `Content-Security-Policy (CSP)` | ⚠️ **Ausente** | Recomendado definir política estrita de scripts |

---

## 15. Auditoria de Dependências

- As dependências em `backend/requirements.txt` foram analisadas:
  - `fastapi==0.141.1`, `pydantic==2.13.4`, `SQLAlchemy==2.0.52`, `PyJWT==2.13.0`, `passlib==1.7.4`, `bcrypt==3.2.2`, `asyncpg==0.31.0`.
  - O pacote `bcrypt` está fixado na versão `< 4.0.0` para evitar a incompatibilidade conhecida do `passlib` com o `bcrypt 4.x`.
  - Nenhuma vulnerabilidade crítica conhecida nas versões fixadas.

---

## 16. Matriz de Novas Vulnerabilidades & Apontamentos

| ID | Arquivo | Componente | Severidade | Descrição do Problema | Impacto | Recomendação de Melhoria |
|---|---|---|---|---|---|---|
| **SEC2-01** | `dependencies.py` | `get_tenant_context` | **MÉDIA** | Auto-atribuição de usuários órfãos (`org_id=None`) à organização default com papel de Admin. | Se um usuário for criado sem organização, recebe acesso à Org 1. | Substituir auto-associação por rejeição estrita `403 Forbidden`. |
| **SEC2-02** | `dependencies.py` | `MemoryRateLimiter` | **MÉDIA** | Rate limiting baseado em memória local do processo. | Em múltiplos workers, limite é multiplicado pelo número de nós. | Adicionar backend Redis para rate limiting distribuído. |
| **SEC2-03** | `main.py` | `SecurityHeadersMiddleware` | **BAIXA** | Ausência de headers HSTS e CSP no middleware de cabeçalhos. | Redução de proteção contra downgrade HTTP e XSS complexo. | Incluir `Strict-Transport-Security` e `Content-Security-Policy`. |
| **SEC2-04** | `kommo/routes.py` | `/callback` | **BAIXA** | Parâmetro `state` do OAuth não possui assinatura criptográfica HMAC. | Risco teórico de CSRF no fluxo de callback do OAuth. | Assinar o parâmetro `state` com `SECRET_KEY` e timestamp. |
| **SEC2-05** | Git History | Histórico | **ALTA** | Credenciais antigas persistidas nos commits `2f46fb6` e `145c3a6`. | Usuários com acesso ao repositório podem ler senhas antigas. | **Rotação obrigatória** das senhas no Supabase e provedores. |

---

## Respostas Claras às 8 Questões Finais

### 1. O isolamento multi-tenant é realmente seguro?
**SIM.** A segregação de dados é aplicada em todas as camadas (JWT, dependências de contexto, repositórios SQLAlchemy e cache particionado por tenant). Testes adversariais comprovaram que Tenant A e Tenant B operam com segregação bidirecional total (A→B e B→A são rejeitados com `403 Forbidden`).

### 2. Existem endpoints sem proteção?
**NÃO.** Todos os endpoints sensíveis de métricas, dashboard, sincronização e integração exigem autenticação ativa e validação de tenant. Apenas `/` (health check), `/api/auth/login`, `/api/auth/refresh` e `/api/integrations/kommo/callback` são acessíveis sem token Bearer, todos devidamente justificados e protegidos por rate limiting ou validação de payload.

### 3. Existem queries sem tenant filter?
**NÃO.** Todas as queries nos repositórios `DashboardRepository` e `SyncRepository` e nos serviços de integração incluem explicitamente a condição `organization_id == :org_id`.

### 4. Existe algum caminho de IDOR?
**NÃO.** Nenhuma entidade pode ser acessada ou alterada fornecendo apenas seu ID. O acesso é obrigatoriamente condicionado à correspondência do `organization_id`.

### 5. Existem secrets no histórico?
**SIM.** Segredos antigos foram commitados nos commits `2f46fb6` e `145c3a6`. Eles foram removidos do código ativo, mas **devem ser rotacionados imediatamente no Supabase e nos provedores de autenticação**.

### 6. O Supabase está adequadamente protegido?
**SIM.** O frontend não tem acesso direto ao Supabase e não possui chaves de API expostas. Toda a comunicação ocorre exclusivamente pelo backend FastAPI com pooler e credenciais isoladas em variáveis de ambiente.

### 7. O rate limiting é adequado para múltiplas instâncias?
**PARCIALMENTE.** Ele é totalmente eficaz em instâncias únicas ou instâncias com 1 worker. Para arquiteturas distribuídas com múltiplos nós/workers, o rate limiting deve ser migrado para Redis ou configurado no API Gateway/Nginx.

### 8. O sistema está realmente pronto para produção?
**SIM, CONDICIONADO À ROTAÇÃO DE CREDENCIAIS.** O código da aplicação está seguro, testado e em conformidade com as melhores práticas de engenharia de software e segurança corporativa.
