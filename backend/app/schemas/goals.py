from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class GoalCreate(BaseModel):
    period_month: str = Field(..., pattern=r"^\d{4}-\d{2}$") # YYYY-MM
    consultora_id: Optional[int] = None
    revenue_target: float = Field(0.0, ge=0)
    leads_target: int = Field(0, ge=0)
    sales_target: int = Field(0, ge=0)
    marketing_investment: float = Field(0.0, ge=0)
    fixed_costs: float = Field(0.0, ge=0)
    notes: Optional[str] = None

class GoalUpdate(BaseModel):
    revenue_target: Optional[float] = Field(None, ge=0)
    leads_target: Optional[int] = Field(None, ge=0)
    sales_target: Optional[int] = Field(None, ge=0)
    marketing_investment: Optional[float] = Field(None, ge=0)
    fixed_costs: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    period_month: str
    consultora_id: Optional[int] = None
    consultora_name: Optional[str] = None
    revenue_target: float
    leads_target: int
    sales_target: int
    marketing_investment: float
    fixed_costs: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class GoalSummaryResponse(BaseModel):
    period_month: str
    revenue_target: float
    actual_revenue: float
    revenue_achievement_pct: float
    leads_target: int
    actual_leads: int
    leads_achievement_pct: float
    sales_target: int
    actual_sales: int
    sales_achievement_pct: float
    marketing_investment: float
    cac: float # Custo de Aquisição de Clientes (Investimento / Vendas Realizadas)
    roi: float # Retorno sobre investimento (Receita / Investimento)
    roas: float
    goals: List[GoalResponse]
