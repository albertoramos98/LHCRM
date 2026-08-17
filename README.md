# LHCRM Pro — Multi-Tenant Executive Analytics & CRM Integration

![LHCRM Banner](https://img.shields.io/badge/LHCRM-Executive_Dashboard-06b6d4?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-3ECF8E?style=for-the-badge&logo=postgresql&logoColor=white)
![MultiTenant](https://img.shields.io/badge/Architecture-Multi--Tenant-8b5cf6?style=for-the-badge)

Plataforma SaaS B2B corporativa de alta performance inspirada nos padrões visuais da **Linear, Vercel e Stripe**. O **LHCRM Pro** oferece um Dashboard Administrativo e Executivo completo com isolamento **Multi-Tenant nativo**, sincronização remota via **OAuth 2.0 com a API do Kommo CRM** e persistência de dados em **PostgreSQL** (compatível com Supabase Pooler).

---

## 🏛️ Arquitetura do Sistema

```text
React 18 + Vite (Frontend)
   │
   │  HTTPS / REST / Bearer JWT + X-Organization-ID
   ▼
FastAPI 0.115+ (Security Headers, Rate Limiting, RBAC & Multi-Tenant Dependency)
   │
   ├──> Domain Services (KommoSyncService, DashboardService, HTMLGenerator)
   │       │
   │       └──> Repositories (SyncRepository, DashboardRepository com Tenant Scoping)
   │               │
   │               └──> PostgreSQL / SQLite (Alembic Migrations)
   │
   └──> Kommo CRM Integration (OAuth 2.0 Per-Tenant, Auto-Refresh & Auto-Sync)
```

---

## ✨ Principais Funcionalidades

### 🏢 Multi-Tenancy Nativo & Isolamento Rigoroso
- **Segregação Completa de Dados:** Nenhuma organização acessa dados de outra.
- **Cache Isolado por Tenant:** Chaves em memória particionadas por ID de organização.
- **Integração OAuth por Organização:** Cada tenant conecta seu próprio subdomínio e chaves de API.
- **Controle de Acesso Baseado em Funções (RBAC):** Papéis `Owner`, `Admin`, `Gerente` e `Consultora`.

### 🔐 Segurança em Nível de Produção
- **Autenticação JWT com Refresh Tokens e Validação de Inatividade.**
- **Rate Limiting em Memória:** Proteção contra ataques de força bruta em `/api/auth/login` e `/api/sync/now`.
- **Prevenção de IDOR e Enumeração de Usuários.**
- **Security Headers:** `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`.
- **CORS Estrito e Segredos 100% Sanitizados:** Variáveis de ambiente isoladas e fora do Git.

### 📊 Dashboard Analítico & Métricas Executivas
- **Módulos:** Visão Geral, Atendimento & Eficiência, Ticket Médio, Receita & Faturamento, Funil de Vendas, Motivos de Perda, Ranking de Consultoras, Follow-up & Tarefas e Origens de Tráfego.
- **Exportação Multiformato:** CSV / Excel, PDF e Dashboard HTML Autônomo com dados embutidos.

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11+ / FastAPI**
- **SQLAlchemy 2.0 (Async Engine)**
- **Alembic (Migrações Versionadas)**
- **asyncpg / aiosqlite**
- **PyJWT & Passlib (Bcrypt)**
- **APScheduler (Agendador Multi-Tenant)**
- **Pytest & Pytest-Asyncio**

### Frontend
- **React 18** + **Vite**
- **TypeScript**
- **TailwindCSS** + **Glassmorphic Tokens**
- **Recharts** (Gráficos analíticos de alta densidade)
- **Lucide Icons**

---

## 💻 Como Executar Localmente

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # Windows (PowerShell)
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt

# Aplicar migrações do banco de dados
alembic upgrade head

# Inicializar servidor em desenvolvimento
uvicorn app.main:app --reload --port 8000
```
- 👉 API: `http://localhost:8000`
- 👉 Documentação Swagger: `http://localhost:8000/docs`

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```
- 👉 Dashboard UI: `http://localhost:3000`

---

## 🧪 Execução de Testes Automatizados

O sistema conta com 20 testes defensivos automatizados cobrindo autenticação, RBAC, isolamento multi-tenant, prevenção contra IDOR, renovação de tokens e serviços de dashboard:

```bash
cd backend
.\.venv\Scripts\pytest.exe -v
```

---

## 🔧 Ferramentas Administrativas (CLI)

O backend inclui utilitários CLI para tarefas administrativas seguras:

```bash
# Criar ou redefinir a organização inicial e administrador
python -m app.cli seed-admin --org-name "Assessoria Revon" --org-slug "revon" --admin-name "Administrador" --admin-email "admin@lhcrm.com" --admin-password "SenhaSegura123!"

# Provisionar uma nova organização tenant
python -m app.cli create-org --name "Clínica Nova" --slug "clinicanova"
```

---

## 📚 Documentação Técnica Completa

- [AUDIT_REPORT.md](file:///c:/Users/alberto/Desktop/LHCRM/AUDIT_REPORT.md) — Relatório Final de Auditoria e Remediações.
- [ARCHITECTURE.md](file:///c:/Users/alberto/Desktop/LHCRM/ARCHITECTURE.md) — Arquitetura de Software e Fluxos de Dados.
- [DATABASE.md](file:///c:/Users/alberto/Desktop/LHCRM/DATABASE.md) — Modelagem de Dados, Relacionamentos e Índices.
- [SECURITY.md](file:///c:/Users/alberto/Desktop/LHCRM/SECURITY.md) — Política de Segurança, Hardening e RBAC.
- [MULTI_TENANCY.md](file:///c:/Users/alberto/Desktop/LHCRM/MULTI_TENANCY.md) — Arquitetura e Garantias Multi-Tenant.
- [DEPLOYMENT.md](file:///c:/Users/alberto/Desktop/LHCRM/DEPLOYMENT.md) — Guia de Implantação e Produção.
- [MIGRATIONS.md](file:///c:/Users/alberto/Desktop/LHCRM/MIGRATIONS.md) — Gerenciamento de Migrações com Alembic.
- [BACKUP_AND_RECOVERY.md](file:///c:/Users/alberto/Desktop/LHCRM/BACKUP_AND_RECOVERY.md) — Rotinas de Backup e DRP.
- [PRIVACY.md](file:///c:/Users/alberto/Desktop/LHCRM/PRIVACY.md) — Conformidade com LGPD e Privacidade.
