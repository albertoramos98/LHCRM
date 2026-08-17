# Arquitetura Multi-Tenancy — LHCRM Pro

## 1. Princípios do Isolamento Multi-Tenant

O LHCRM Pro foi concebido para atender múltiplos clientes e empresas (**Tenants**) com garantia matemática de isolamento de dados:

1. **Cliente A nunca vê dados do Cliente B:** Todas as operações de leitura, escrita, atualização, exclusão e agregação analítica são vinculadas ao `organization_id` autenticado.
2. **Isolamento de Cache em Memória:** As chaves de cache do dashboard incluem o prefixo da organização (`org:{organization_id}:overview:...`), impedindo vazamento de dados via cache compartilhado.
3. **Isolamento de Integrações de CRM:** Cada empresa possui suas próprias credenciais, subdomínio e tokens OAuth do Kommo CRM na tabela `crm_integrations`.
4. **Agendador de Sincronização Per-Tenant:** O cron assíncrono itera sobre as organizações ativas e executa sincronizações isoladas para cada empresa.

---

## 2. Modelagem de Associação e Acesso

- Um usuário (`User`) possui uma organização principal (`organization_id`) e pode pertencer a múltiplas organizações através da tabela associativa `organization_members`.
- Em cada organização, o usuário possui um papel específico (`Owner`, `Admin`, `Gerente`, `Consultora`).

```
                    ┌─────────────────────────┐
                    │      Organization       │
                    │ (id: 1, slug: 'alpha')  │
                    └───────────┬─────────────┘
                                │ 1:N
                    ┌───────────▼─────────────┐
                    │   OrganizationMember    │
                    │   (role: 'Admin')       │
                    └───────────▲─────────────┘
                                │ N:1
                    ┌───────────┴─────────────┐
                    │          User           │
                    │   (id: 10, email: ...)  │
                    └─────────────────────────┘
```

---

## 3. Resolução de Tenancy nas Requisições

A resolução de contexto do tenant é feita de forma estrita pela dependência `get_tenant_context`:

1. O cliente pode enviar o cabeçalho `X-Organization-ID: <id>` (ou o sistema adota a organização primária do usuário autenticado).
2. O backend valida se o usuário autenticado é membro ativo da organização solicitada.
3. Se o usuário não pertencer à organização, a requisição é imediatamente interrompida com `403 Forbidden: Acesso negado. Você não possui permissão nesta organização.`
4. O objeto `TenantContext` injetado no controller contém `tenant.organization_id`, garantindo que todas as consultas subsequentes utilizem essa chave.

---

## 4. Criação de Novos Tenants (Provisionamento)

Novas empresas podem ser provisionadas de forma programática ou via CLI administrativo:

```bash
python -m app.cli create-org --name "Clínica Vida Nova" --slug "vidanova"
```
