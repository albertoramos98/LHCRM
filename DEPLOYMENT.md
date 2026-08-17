# Guia de Implantação e Deploy em Produção — LHCRM Pro

## 1. Pré-Requisitos

- **Docker & Docker Compose** (versão 24+) OU Python 3.11+ e Node.js 18+
- **PostgreSQL 15+** (Supabase, AWS RDS, DigitalOcean ou servidor dedicado)
- Domínio configurado com certificado SSL/TLS (HTTPS obrigatório)

---

## 2. Configuração das Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto com base no `.env.example`:

```bash
# Ambiente
ENVIRONMENT=production

# Segurança Criptográfica (obrigatório: gerar com 'openssl rand -hex 32')
SECRET_KEY=e8392fbc09d172e9a218d83920194821a839d0124810a0129f81a02938102938
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=30

# Banco de Dados PostgreSQL de Produção (com suporte a Pooler / Transaction Mode)
DATABASE_URL=postgresql+asyncpg://postgres.meuprojeto:MinhaSenhaSegura123@aws-0-sa-east-1.pooler.supabase.com:6543/postgres

# CORS e URLs de Produção
ALLOWED_ORIGINS=https://app.lhcrm.com.br,https://api.lhcrm.com.br
FRONTEND_URL=https://app.lhcrm.com.br

# Integração Kommo CRM (OAuth Provedor)
KOMMO_CLIENT_ID=meu_kommo_client_id
KOMMO_CLIENT_SECRET=meu_kommo_client_secret
KOMMO_REDIRECT_URI=https://api.lhcrm.com.br/api/integrations/kommo/callback

# Administrador Inicial
INITIAL_ADMIN_EMAIL=admin@lhcrm.com.br
INITIAL_ADMIN_PASSWORD=SenhaAdminForte2026!#
```

---

## 3. Deploy via Docker Compose

Execute o build e a inicialização dos contêineres:

```bash
docker compose build --no-cache
docker compose up -d
```

Verifique os logs dos serviços:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

---

## 4. Execução de Migrações em Produção

Após iniciar o container do backend, execute o upgrade do Alembic:

```bash
docker compose exec backend alembic upgrade head
```

---

## 5. Inicialização / Bootstrap do Administrador Inicial

Para criar a organização padrão e a conta do administrador:

```bash
docker compose exec backend python -m app.cli seed-admin \
  --org-name "Assessoria Revon" \
  --org-slug "revon" \
  --admin-name "Administrador" \
  --admin-email "admin@lhcrm.com.br" \
  --admin-password "SenhaForteDefinidaAqui123!"
```
