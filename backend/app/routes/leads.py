from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_tenant_context, TenantContext, require_role
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse, CsvImportSummary
from app.services.lead_service import LeadService

router = APIRouter(prefix="/api/leads", tags=["Lead & Sales Management"])

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Manually creates a new lead or closed deal scoped to the active tenant.
    """
    service = LeadService(db, organization_id=tenant.organization_id)
    return await service.create_lead(payload, current_user_id=tenant.user_id)

@router.get("", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    source_type: Optional[str] = None,
    consultora_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    status_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Lists leads with pagination, search, and source_type filtering.
    """
    # Role-based restriction: Consultoras only see their own leads unless manager
    effective_consultora_id = tenant.user_id if tenant.role == "Consultora" else consultora_id
    service = LeadService(db, organization_id=tenant.organization_id)
    return await service.list_leads(
        page=page,
        page_size=page_size,
        search=search,
        source_type=source_type,
        consultora_id=effective_consultora_id,
        pipeline_id=pipeline_id,
        status_id=status_id
    )

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Retrieves details for a specific lead within the tenant.
    """
    service = LeadService(db, organization_id=tenant.organization_id)
    lead = await service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead não encontrado")
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Updates lead status, price, or details within tenant boundary.
    """
    service = LeadService(db, organization_id=tenant.organization_id)
    updated = await service.update_lead(lead_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead não encontrado")
    return updated

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_role(["Owner", "Admin", "Gerente"]))
):
    """
    Deletes a lead (requires Admin or Manager role).
    """
    service = LeadService(db, organization_id=tenant.organization_id)
    success = await service.delete_lead(lead_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead não encontrado")
    return None

@router.post("/import-csv", response_model=CsvImportSummary)
async def import_csv_leads(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_role(["Owner", "Admin", "Gerente"]))
):
    """
    Bulk import leads from a CSV spreadsheet file.
    """
    if not file.filename.lower().endswith(('.csv', '.txt')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de arquivo inválido. Envie um arquivo .csv")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024: # 10MB limit
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo excede o limite de 10MB")

    service = LeadService(db, organization_id=tenant.organization_id)
    return await service.import_csv(content)
