from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.domain import User
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == req.email))
    user = res.scalar_one_or_none()

    # Seed initial admin user if none exists
    if not user and req.email == "admin@empresa.com":
        user = User(
            name="Administrador Executive",
            email="admin@empresa.com",
            hashed_password=get_password_hash("admin123"),
            role="Admin",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user or not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Verifique e-mail e senha."
        )

    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido ou expirado.")

    user_id = payload.get("sub")
    res = await db.execute(select(User).where(User.id == int(user_id)))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")

    access_token = create_access_token(subject=user.id, role=user.role)
    new_refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role
    )
