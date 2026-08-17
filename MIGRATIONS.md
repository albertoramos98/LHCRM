# Guia de Migrações de Banco de Dados — LHCRM Pro

## 1. Estratégia de Migrações com Alembic

O LHCRM Pro utiliza o **Alembic** configurado com suporte a drivers assíncronos (`asyncpg` / `aiosqlite`).

### Regras de Ouro:
1. **Nunca executar `DROP TABLE` ou `DROP COLUMN` destrutivos sem aprovação formal.**
2. **Sempre escrever migrações reversíveis** (com métodos `upgrade()` e `downgrade()` consistentes).
3. **Estratégia de Backfill Seguro:** Novas colunas obrigatórias com chave estrangeira (como `organization_id`) devem ser adicionadas como anuláveis ou com valor default seguro durante o backfill, para evitar falhas em dados legados.

---

## 2. Histórico de Versões

- **`001_initial_multitenant_schema.py`**:
  - Criação das tabelas base: `organizations`, `users`, `organization_members`, `companies`, `contacts`, `pipelines`, `lead_status`, `tags`, `custom_fields`, `leads`, `lead_tags`, `tasks`, `events`, `lead_history`, `sync_logs`, `crm_integrations`, `integration_logs`.
  - Criação de chaves estrangeiras com regras de integridade referencial (`CASCADE` / `SET NULL`).
  - Criação de índices de performance e constraints de unicidade composta `(organization_id, external_id)`.

- **`002_safe_backfill_and_tenant_indexes.py`**:
  - Provisionamento da organização default (`slug='default'`) se não existente.
  - Backfill seguro de registros legados associando-os à organização default.
  - Criação automática dos registros de associação de membros (`organization_members`).

---

## 3. Comandos Úteis do Alembic

```bash
# Aplicar todas as migrações pendentes
alembic upgrade head

# Reverter a última migração
alembic downgrade -1

# Verificar a revisão atual do banco
alembic current

# Gerar uma nova revisão automática baseada nos modelos SQLAlchemy
alembic revision --autogenerate -m "descricao_da_alteracao"
```
