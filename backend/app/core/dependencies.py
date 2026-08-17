import time
import abc
from collections import defaultdict
from typing import Optional, List, Dict, Tuple
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.domain import User, Organization, OrganizationMember
from app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)

# ==============================================================================
# Rate Limiter Abstraction
# ==============================================================================

class BaseRateLimiter(abc.ABC):
    @abc.abstractmethod
    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """Returns True if request is allowed, False if rate limit exceeded."""
        pass

class MemoryRateLimiter(BaseRateLimiter):
    """
    In-memory rate limiter suitable for single-instance or single-worker deployments.
    Tracks timestamps per key and purges expired windows on access.
    """
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        window_start = now - window_seconds
        # Clean old timestamps outside sliding window
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        if len(self.requests[key]) >= max_requests:
            return False
        self.requests[key].append(now)
        return True

class RedisRateLimiter(BaseRateLimiter):
    """
    Redis-backed rate limiter for distributed, multi-instance deployments.
    Architecture blueprint for horizontal scaling.
    """
    def __init__(self, redis_client=None):
        self.redis = redis_client

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        if not self.redis:
            # Fallback to permissive if redis is not initialized in dev
            return True
        # Sliding window log algorithm using Redis ZSET
        now = time.time()
        window_start = now - window_seconds
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_seconds)
        results = pipe.execute()
        current_count = results[1]
        return current_count < max_requests

# Default active rate limiter instance
rate_limiter: BaseRateLimiter = MemoryRateLimiter()

def rate_limit_login(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    key = f"login:{client_ip}"
    if not rate_limiter.check_rate_limit(key, max_requests=settings.RATE_LIMIT_LOGIN_PER_MINUTE, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de login. Por favor, aguarde um minuto antes de tentar novamente."
        )

def rate_limit_sync(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    key = f"sync:{client_ip}"
    if not rate_limiter.check_rate_limit(key, max_requests=settings.RATE_LIMIT_SYNC_PER_MINUTE, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite de sincronizações manuais excedido. Por favor, aguarde um minuto."
        )

# ==============================================================================
# Authentication & Tenant Dependencies
# ==============================================================================

async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária. Token Bearer ausente.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = auth.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, expirado ou não autorizado.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token com formato inválido (sub ausente)."
        )

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuário inválido."
        )

    res = await db.execute(select(User).where(User.id == user_id_int))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário associado a este token não foi encontrado."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Acesso bloqueado."
        )

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário inativa."
        )
    return current_user

class TenantContext:
    def __init__(self, organization: Organization, user: User, member: Optional[OrganizationMember] = None):
        self.organization = organization
        self.organization_id = organization.id
        self.user = user
        self.user_id = user.id
        self.role = member.role if member else user.role

async def get_tenant_context(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    x_organization_id: Optional[str] = Header(None)
) -> TenantContext:
    """
    Resolves active tenant organization for current authenticated user.
    Strictly enforces that user belongs to the target organization.
    NO AUTOMATIC PROVISIONING OR FALLBACK TO DEFAULT ORG FOR ORPHAN USERS.
    """
    target_org_id = None
    if x_organization_id:
        try:
            target_org_id = int(x_organization_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cabeçalho X-Organization-ID inválido.")
    elif current_user.organization_id:
        target_org_id = current_user.organization_id
    else:
        # Check explicit membership table
        member_res = await db.execute(
            select(OrganizationMember).where(OrganizationMember.user_id == current_user.id).limit(1)
        )
        membership = member_res.scalar_one_or_none()
        if membership:
            target_org_id = membership.organization_id

    # If user has no organization associated anywhere -> REJECT with 403 Forbidden
    if not target_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Usuário não associado a nenhuma organização válida."
        )

    # Fetch Organization and verify it is active
    res_org = await db.execute(select(Organization).where(Organization.id == target_org_id, Organization.is_active == True))
    organization = res_org.scalar_one_or_none()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Organização não encontrada ou inativa."
        )

    # Check member record or primary organization match
    res_mem = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization.id,
            OrganizationMember.user_id == current_user.id
        )
    )
    membership = res_mem.scalar_one_or_none()
    if not membership and current_user.organization_id != organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você não possui permissão nesta organização."
        )

    return TenantContext(organization=organization, user=current_user, member=membership)

def require_role(allowed_roles: List[str]):
    async def role_checker(
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> TenantContext:
        user_role = tenant_context.role
        # Owner / Admin always has full access
        if user_role in ["Owner", "Admin"]:
            return tenant_context
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão insuficiente. Esta ação requer um dos seguintes perfis: {', '.join(allowed_roles)}."
            )
        return tenant_context
    return role_checker

async def require_admin(
    tenant_context: TenantContext = Depends(get_tenant_context)
) -> TenantContext:
    if tenant_context.role not in ["Owner", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito apenas a administradores da organização."
        )
    return tenant_context
