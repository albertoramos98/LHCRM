from typing import Optional
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_token
from app.services.dashboard_service import DashboardService
from app.models.domain import User, Pipeline, LeadStatus, Lead

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard Executive Metrics"])

async def get_current_user_info(authorization: Optional[str] = Header(None)) -> tuple[str, Optional[int]]:
    if not authorization or not authorization.startswith("Bearer "):
        return "Admin", None
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return "Admin", None
    user_role = payload.get("role", "Admin")
    user_id = payload.get("sub")
    return user_role, int(user_id) if user_id else None

@router.get("/options")
async def get_filter_options(db: AsyncSession = Depends(get_db)):
    """
    Returns populated options for filter dropdowns (Consultoras, Pipelines, Statuses, Unidades, Procedimentos, Origens, Suborigens).
    """
    users_res = await db.execute(select(User.id, User.name).where(User.is_active == True))
    consultoras = [{"id": u[0], "name": u[1]} for u in users_res.all()]

    pipes_res = await db.execute(select(Pipeline.id, Pipeline.name))
    pipelines = [{"id": p[0], "name": p[1]} for p in pipes_res.all()]

    statuses_res = await db.execute(select(LeadStatus.id, LeadStatus.name, LeadStatus.pipeline_id))
    statuses = [{"id": s[0], "name": s[1], "pipeline_id": s[2]} for s in statuses_res.all()]

    units_res = await db.execute(select(Lead.unidade).where(Lead.unidade.isnot(None)).distinct())
    unidades = [u[0] for u in units_res.all() if u[0]]

    procs_res = await db.execute(select(Lead.procedimento).where(Lead.procedimento.isnot(None)).distinct())
    procedimentos = [p[0] for p in procs_res.all() if p[0]]

    origs_res = await db.execute(select(Lead.origem).where(Lead.origem.isnot(None)).distinct())
    origens = [o[0] for o in origs_res.all() if o[0]]

    suborigs_res = await db.execute(select(Lead.suborigem).where(Lead.suborigem.isnot(None)).distinct())
    suborigens = [s[0] for s in suborigs_res.all() if s[0]]

    return {
        "consultoras": consultoras,
        "pipelines": pipelines,
        "statuses": statuses,
        "unidades": unidades,
        "procedimentos": procedimentos,
        "origens": origens,
        "suborigens": suborigens
    }

@router.get("/overview")
async def get_overview(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    status_id: Optional[int] = None,
    unidade: Optional[str] = None,
    procedimento: Optional[str] = None,
    origem: Optional[str] = None,
    suborigem: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_overview(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id, status_id=status_id,
        unidade=unidade, procedimento=procedimento, origem=origem, suborigem=suborigem,
        user_role=role, current_user_id=user_id
    )

@router.get("/funnel")
async def get_funnel(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    status_id: Optional[int] = None,
    unidade: Optional[str] = None,
    procedimento: Optional[str] = None,
    origem: Optional[str] = None,
    suborigem: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_funnel(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id, status_id=status_id,
        unidade=unidade, procedimento=procedimento, origem=origem, suborigem=suborigem,
        user_role=role, current_user_id=user_id
    )

@router.get("/revenue")
async def get_revenue(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    status_id: Optional[int] = None,
    unidade: Optional[str] = None,
    procedimento: Optional[str] = None,
    origem: Optional[str] = None,
    suborigem: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_revenue(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id, status_id=status_id,
        unidade=unidade, procedimento=procedimento, origem=origem, suborigem=suborigem,
        user_role=role, current_user_id=user_id
    )

@router.get("/followup")
async def get_followup(
    period: str = Query("30days"),
    consultora_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_followup(
        period=period, consultora_id=consultora_id,
        user_role=role, current_user_id=user_id
    )

@router.get("/ranking")
async def get_ranking(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pipeline_id: Optional[int] = None,
    unidade: Optional[str] = None,
    procedimento: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_ranking(
        period=period, start_date=start_date, end_date=end_date,
        pipeline_id=pipeline_id, unidade=unidade, procedimento=procedimento,
        user_role=role, current_user_id=user_id
    )

@router.get("/losses")
async def get_losses(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    unidade: Optional[str] = None,
    procedimento: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_losses(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id,
        unidade=unidade, procedimento=procedimento,
        user_role=role, current_user_id=user_id
    )

@router.get("/origins")
async def get_origins(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    unidade: Optional[str] = None,
    procedimento: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_origins(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id,
        unidade=unidade, procedimento=procedimento,
        user_role=role, current_user_id=user_id
    )

@router.get("/tickets")
async def get_tickets(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    unidade: Optional[str] = None,
    procedimento: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_tickets(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id,
        unidade=unidade, procedimento=procedimento,
        user_role=role, current_user_id=user_id
    )

@router.get("/performance")
async def get_performance(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_performance(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id,
        user_role=role, current_user_id=user_id
    )

@router.get("/metrics")
async def get_all_metrics(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    status_id: Optional[int] = None,
    unidade: Optional[str] = None,
    procedimento: Optional[str] = None,
    origem: Optional[str] = None,
    suborigem: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_info: tuple[str, Optional[int]] = Depends(get_current_user_info)
):
    role, user_id = user_info
    service = DashboardService(db)
    return await service.get_all_metrics(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id, status_id=status_id,
        unidade=unidade, procedimento=procedimento, origem=origem, suborigem=suborigem,
        user_role=role, current_user_id=user_id
    )
