import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.dependencies import get_current_active_user, rate_limit_login, get_tenant_context, TenantContext
import re
import uuid
from app.models.domain import User, Organization, OrganizationMember, Pipeline, LeadStatus
from app.schemas.auth import (
    LoginRequest,
    RegisterOrganizationRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    OrganizationInfo
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-') or 'empresa'

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_organization(
    req: RegisterOrganizationRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new tenant organization with its admin owner and bootstraps initial pipelines.
    """
    normalized_email = req.email.strip().lower()

    # Check if user already exists
    existing_user_res = await db.execute(select(User).where(User.email == normalized_email))
    if existing_user_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma conta cadastrada com este e-mail. Faça login ou use outro e-mail."
        )

    # Determine unique organization slug
    base_slug = slugify(req.slug or req.company_name)
    slug = base_slug
    org_res = await db.execute(select(Organization).where(Organization.slug == slug))
    if org_res.scalar_one_or_none():
        slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"

    # 1. Create Organization
    org = Organization(
        name=req.company_name.strip(),
        slug=slug,
        is_active=True
    )
    db.add(org)
    await db.flush()

    # 2. Create Admin Owner User
    hashed_pwd = get_password_hash(req.password)
    user = User(
        name=req.admin_name.strip(),
        email=normalized_email,
        hashed_password=hashed_pwd,
        role="Owner",
        organization_id=org.id,
        is_active=True
    )
    db.add(user)
    await db.flush()

    # 3. Create Organization Membership
    membership = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role="Owner"
    )
    db.add(membership)

    # 4. Bootstrap Default Pipeline and Stages
    pipe = Pipeline(
        organization_id=org.id,
        name="Funil de Vendas",
        is_main=True,
        sort_order=1
    )
    db.add(pipe)
    await db.flush()

    stages = [
        {"name": "Novo Lead", "sort_order": 1, "type": 1, "color": "#06b6d4"},
        {"name": "Em Atendimento", "sort_order": 2, "type": 1, "color": "#3b82f6"},
        {"name": "Negociação", "sort_order": 3, "type": 1, "color": "#8b5cf6"},
        {"name": "Ganhos", "sort_order": 4, "type": 2, "color": "#10b981"},
        {"name": "Perdidos", "sort_order": 5, "type": 3, "color": "#ef4444"},
    ]
    for stg in stages:
        status_obj = LeadStatus(
            organization_id=org.id,
            pipeline_id=pipe.id,
            name=stg["name"],
            sort_order=stg["sort_order"],
            type=stg["type"],
            color=stg["color"]
        )
        db.add(status_obj)

    await db.commit()
    await db.refresh(user)
    await db.refresh(org)

    # 5. Issue Tokens
    access_token = create_access_token(subject=user.id, role=user.role, organization_id=org.id)
    refresh_token = create_refresh_token(subject=user.id, organization_id=org.id)

    is_prod = settings.ENVIRONMENT.lower() == "production"
    response.set_cookie(
        key="lhcrm_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth"
    )

    logger.info(f"New multi-tenant organization created: {org.name} (Slug: {org.slug}, Owner: {user.email})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        organization=OrganizationInfo(id=org.id, name=org.name, slug=org.slug)
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    # Enforce rate limiting on login attempts
    rate_limit_login(request)

    # Normalize email/username
    normalized_email = req.email.strip().lower()

    res = await db.execute(select(User).where(User.email == normalized_email))
    user = res.scalar_one_or_none()

    # Generic invalid credentials response to prevent user enumeration
    invalid_credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas. Verifique seu e-mail e senha."
    )

    if not user or not user.hashed_password:
        raise invalid_credentials_exc

    if not verify_password(req.password, user.hashed_password):
        raise invalid_credentials_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário inativa. Entre em contato com o administrador."
        )

    # Resolve organization info
    org_info = None
    org_id = user.organization_id

    if org_id:
        org_res = await db.execute(select(Organization).where(Organization.id == org_id))
        org = org_res.scalar_one_or_none()
        if org:
            org_info = OrganizationInfo(id=org.id, name=org.name, slug=org.slug)
    else:
        # Check explicit membership table
        mem_res = await db.execute(select(OrganizationMember).where(OrganizationMember.user_id == user.id).limit(1))
        mem = mem_res.scalar_one_or_none()
        if mem:
            org_res = await db.execute(select(Organization).where(Organization.id == mem.organization_id))
            org = org_res.scalar_one_or_none()
            if org:
                org_id = org.id
                org_info = OrganizationInfo(id=org.id, name=org.name, slug=org.slug)

    access_token = create_access_token(subject=user.id, role=user.role, organization_id=org_id)
    refresh_token = create_refresh_token(subject=user.id, organization_id=org_id)

    # Set secure HttpOnly cookie for refresh token
    is_prod = settings.ENVIRONMENT.lower() == "production"
    response.set_cookie(
        key="lhcrm_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth"
    )

    logger.info(f"Successful login for user {user.email} (ID: {user.id}, Org ID: {org_id})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        organization=org_info
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    req: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    # Extract token from request body OR from HttpOnly cookie
    raw_token = None
    if req and req.refresh_token:
        raw_token = req.refresh_token
    else:
        raw_token = request.cookies.get("lhcrm_refresh_token")

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token não fornecido (nem via corpo JSON nem via Cookie HttpOnly)."
        )

    payload = decode_token(raw_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado."
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido."
        )

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

    res = await db.execute(select(User).where(User.id == user_id_int))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário inativa. Acesso bloqueado."
        )

    org_id = payload.get("org_id") or user.organization_id
    org_info = None
    if org_id:
        org_res = await db.execute(select(Organization).where(Organization.id == org_id))
        org = org_res.scalar_one_or_none()
        if org:
            org_info = OrganizationInfo(id=org.id, name=org.name, slug=org.slug)

    access_token = create_access_token(subject=user.id, role=user.role, organization_id=org_id)
    new_refresh_token = create_refresh_token(subject=user.id, organization_id=org_id)

    # Refresh the HttpOnly cookie
    is_prod = settings.ENVIRONMENT.lower() == "production"
    response.set_cookie(
        key="lhcrm_refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth"
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        organization=org_info
    )

@router.post("/logout")
async def logout(response: Response):
    """
    Clears the HttpOnly refresh token cookie on user logout.
    """
    response.delete_cookie(key="lhcrm_refresh_token", path="/api/auth")
    return {"status": "success", "message": "Logout realizado com sucesso."}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user
