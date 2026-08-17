# Guia de Segurança e Hardening — LHCRM Pro

## 1. Modelo de Ameaças & Vetores Protegidos

O LHCRM Pro adota uma postura de segurança defensiva em profundidade (**Defense in Depth**):

1. **Prevenção de IDOR (Insecure Direct Object Reference):** Nenhuma entidade é acessada puramente por ID primário. Toda consulta no banco é vinculada à verificação `organization_id == active_tenant.id`.
2. **Defesa contra Enumeração de Usuários:** Endpoints de login respondem com mensagens e status codes genéricos (`401 Credenciais inválidas`).
3. **Controle de Força Bruta (Brute-Force / DoS):** Rate limiters em memória protegem `/api/auth/login` (máximo 10 requisições/min por IP) e `/api/sync/now` (máximo 5 requisições/min por IP).
4. **Proteção de Segredos em Trânsito:** Tokens e segredos nunca são passados em query strings de URLs ou logs de servidor.
5. **CORS Restrito:** Origens permitidas são configuradas estritamente via variável de ambiente `ALLOWED_ORIGINS` (evitando wildcards com credenciais).
6. **Segurança de Cabeçalhos HTTP:** Middleware `SecurityHeadersMiddleware` injeta:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: SAMEORIGIN`
   - `X-XSS-Protection: 1; mode=block`
   - `Referrer-Policy: strict-origin-when-cross-origin`

---

## 2. Autenticação & Gestão de Tokens JWT

- **Algoritmo:** HMAC-SHA256 (HS256).
- **Access Token:** Válido por 120 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES`). Contém `sub` (User ID), `role`, `org_id`, `type="access"`, `iat` e `exp`.
- **Refresh Token:** Válido por 30 dias (`REFRESH_TOKEN_EXPIRE_DAYS`). Contém `sub`, `org_id`, `type="refresh"`, `iat` e `exp`.
- **Validação de Inatividade:** A cada refresh ou requisição, o sistema verifica se a conta do usuário ou a organização foram desativadas (`is_active=False`), bloqueando imediatamente o acesso.

---

## 3. Matriz de Autorização RBAC (Role-Based Access Control)

| Funcionalidade / Rota | Owner | Admin | Gerente | Consultora |
|---|:---:|:---:|:---:|:---:|
| Visualizar Dashboard Geral e Métricas | ✅ | ✅ | ✅ | ✅ (Apenas seus leads) |
| Exportar Relatório HTML / CSV / PDF | ✅ | ✅ | ✅ | ✅ |
| Disparar Sincronização Manual (`/sync/now`) | ✅ | ✅ | ✅ | ❌ |
| Conectar / Desconectar Kommo CRM | ✅ | ✅ | ❌ | ❌ |
| Renovar Token de Integração OAuth | ✅ | ✅ | ❌ | ❌ |
| Gerenciar Membros da Organização | ✅ | ✅ | ❌ | ❌ |
| Criar Nova Organização (SaaS) | CLI / SysAdmin | ❌ | ❌ | ❌ |

---

## 4. Gestão de Segredos e Variáveis de Ambiente

Nenhum segredo de produção deve residir no repositório. O arquivo `.env` deve ser mantido fora do controle de versão (`.gitignore`).

Variáveis críticas:
- `SECRET_KEY`: Chave criptográfica aleatória de 256 bits.
- `DATABASE_URL`: URI de conexão ao banco de dados com credenciais seguras.
- `KOMMO_CLIENT_ID` / `KOMMO_CLIENT_SECRET`: Credenciais do desenvolvedor Kommo.
- `ALLOWED_ORIGINS`: Lista separada por vírgula das origens autorizadas (ex: `https://meuapp.com.br`).
