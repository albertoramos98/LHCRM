from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_tenant_context, TenantContext
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard Executive Metrics"])

@router.get("/options")
async def get_filter_options(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Returns populated options for filter dropdowns scoped to current tenant.
    """
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_filter_options()

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
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_overview(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id, status_id=status_id,
        unidade=unidade, procedimento=procedimento, origem=origem, suborigem=suborigem,
        user_role=tenant.role, current_user_id=tenant.user_id
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
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_funnel(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id, status_id=status_id,
        unidade=unidade, procedimento=procedimento, origem=origem, suborigem=suborigem,
        user_role=tenant.role, current_user_id=tenant.user_id
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
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_revenue(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id, status_id=status_id,
        unidade=unidade, procedimento=procedimento, origem=origem, suborigem=suborigem,
        user_role=tenant.role, current_user_id=tenant.user_id
    )

@router.get("/followup")
async def get_followup(
    period: str = Query("30days"),
    consultora_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_followup(
        period=period, consultora_id=consultora_id,
        user_role=tenant.role, current_user_id=tenant.user_id
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
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_ranking(
        period=period, start_date=start_date, end_date=end_date,
        pipeline_id=pipeline_id, unidade=unidade, procedimento=procedimento,
        user_role=tenant.role, current_user_id=tenant.user_id
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
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_losses(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id,
        unidade=unidade, procedimento=procedimento,
        user_role=tenant.role, current_user_id=tenant.user_id
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
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_origins(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id,
        unidade=unidade, procedimento=procedimento,
        user_role=tenant.role, current_user_id=tenant.user_id
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
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_tickets(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id,
        unidade=unidade, procedimento=procedimento,
        user_role=tenant.role, current_user_id=tenant.user_id
    )

@router.get("/performance")
async def get_performance(
    period: str = Query("30days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_performance(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id,
        user_role=tenant.role, current_user_id=tenant.user_id
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
    tenant: TenantContext = Depends(get_tenant_context)
):
    service = DashboardService(db, organization_id=tenant.organization_id)
    return await service.get_all_metrics(
        period=period, start_date=start_date, end_date=end_date,
        consultora_id=consultora_id, pipeline_id=pipeline_id, status_id=status_id,
        unidade=unidade, procedimento=procedimento, origem=origem, suborigem=suborigem,
        user_role=tenant.role, current_user_id=tenant.user_id
    )

@router.get("/export-html")
async def export_dashboard_html(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Generates a standalone executive dashboard HTML file on-the-fly with the
    tenant-specific data embedded, and returns it as a file download.
    """
    import tempfile
    import os
    from app.services.html_generator import generate_dashboard_html

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = os.path.join(tmpdir, f"dashboard_export_org_{tenant.organization_id}.html")
        await generate_dashboard_html(db, organization_id=tenant.organization_id, output_path=tmp_file)
        with open(tmp_file, "r", encoding="utf-8") as f:
            content = f.read()

    headers = {
        "Content-Disposition": f'attachment; filename="dashboard_executivo_{tenant.organization.slug}.html"'
    }
    return Response(content=content, media_type="text/html", headers=headers)
