# Documentação Técnica: Arquitetura de Rate Limiting — LHCRM Pro

## 1. Visão Geral e Abstração

O LHCRM Pro implementa uma camada de proteção contra ataques de força bruta, abuso de API e negação de serviço (DoS) baseada na interface abstrata `BaseRateLimiter` (`app/core/dependencies.py`).

### Endpoints Protegidos
- `POST /api/auth/login`: Máximo 10 requisições por minuto por IP (`RATE_LIMIT_LOGIN_PER_MINUTE`).
- `POST /api/sync/now`: Máximo 5 requisições por minuto por IP (`RATE_LIMIT_SYNC_PER_MINUTE`).

---

## 2. Implementação Atual: `MemoryRateLimiter`

A implementação padrão em execução é a `MemoryRateLimiter`, que opera com uma janela deslizante em memória:

```python
class MemoryRateLimiter(BaseRateLimiter):
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        window_start = now - window_seconds
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        if len(self.requests[key]) >= max_requests:
            return False
        self.requests[key].append(now)
        return True
```

### Características e Comportamento Operacional:
1. **Instância Única / Single Worker:** Funciona com precisão matemática em nível de milissegundos sem dependências de infraestrutura externa.
2. **Ambiente Multi-Worker / Multi-Instância:**
   - Como a memória do processo Python não é compartilhada entre múltiplos processos Uvicorn (`workers > 1`) ou réplicas de contêineres Docker, cada nó mantém sua própria contagem isolada.
   - O número de tentativas permitido por IP antes do bloqueio é multiplicado pelo número de workers/instâncias.

---

## 3. Arquitetura para Escala Horizontal: `RedisRateLimiter`

Para ambientes corporativos distribuídos de alta escala com múltiplos contêineres e balanceador de carga, o sistema já possui a interface arquitetural `RedisRateLimiter` preparada para uso com Redis via ZSET (Sliding Window Log):

```python
class RedisRateLimiter(BaseRateLimiter):
    def __init__(self, redis_client):
        self.redis = redis_client

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        window_start = now - window_seconds
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_seconds)
        results = pipe.execute()
        return results[1] < max_requests
```

### Alternativa Recomendada em Produção:
Adicionalmente, recomenda-se configurar regras de WAF / Rate Limiting na camada de borda (Cloudflare, AWS WAF ou Nginx `limit_req_zone`), bloqueando requisições abusivas antes mesmo de atingirem a camada de aplicação.
