from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_tenant_context, TenantContext, require_role
from app.schemas.goals import GoalCreate, GoalResponse, GoalSummaryResponse
from app.services.goal_service import GoalService

router = APIRouter(prefix="/api/goals", tags=["Goals, CAC & Marketing Analytics"])

@router.post("", response_model=GoalResponse, status_code=status.HTTP_200_OK)
async def create_or_update_goal(
    payload: GoalCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_role(["Owner", "Admin", "Gerente"]))
):
    """
    Creates or updates a monthly revenue/leads target or marketing investment record.
    """
    service = GoalService(db, organization_id=tenant.organization_id)
    return await service.create_or_update_goal(payload)

@router.get("", response_model=List[GoalResponse])
async def list_goals(
    period_month: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Lists all saved goals/marketing spend records.
    """
    service = GoalService(db, organization_id=tenant.organization_id)
    return await service.list_goals(period_month=period_month)

@router.get("/summary", response_model=GoalSummaryResponse)
async def get_goal_summary(
    period_month: Optional[str] = None,
    consultora_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Calculates monthly target achievement (Revenue %, Leads %, Sales %), CAC and ROI.
    """
    if not period_month:
        now = datetime.now(timezone.utc)
        period_month = f"{now.year:04d}-{now.month:02d}"

    service = GoalService(db, organization_id=tenant.organization_id)
    return await service.get_summary(period_month=period_month, consultora_id=consultora_id)

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_role(["Owner", "Admin", "Gerente"]))
):
    """
    Deletes a target/goal record.
    """
    service = GoalService(db, organization_id=tenant.organization_id)
    success = await service.delete_goal(goal_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta não encontrada")
    return None
