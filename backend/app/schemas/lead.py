from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class LeadBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(0.0, ge=0)
    pipeline_id: int
    status_id: int
    responsible_user_id: Optional[int] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    company_name: Optional[str] = None
    unidade: Optional[str] = None
    procedimento: Optional[str] = None
    origem: Optional[str] = None
    suborigem: Optional[str] = None
    loss_reason: Optional[str] = None
    notes: Optional[str] = None
    custom_fields_values: Optional[Dict[str, Any]] = None

class LeadCreate(LeadBase):
    source_type: str = "manual" # manual, csv, etc.

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    pipeline_id: Optional[int] = None
    status_id: Optional[int] = None
    responsible_user_id: Optional[int] = None
    unidade: Optional[str] = None
    procedimento: Optional[str] = None
    origem: Optional[str] = None
    suborigem: Optional[str] = None
    loss_reason: Optional[str] = None
    closed_at: Optional[datetime] = None
    custom_fields_values: Optional[Dict[str, Any]] = None

class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    external_id: Optional[int] = None
    source_type: str
    name: str
    price: float
    pipeline_id: int
    pipeline_name: Optional[str] = None
    status_id: int
    status_name: Optional[str] = None
    responsible_user_id: Optional[int] = None
    responsible_user_name: Optional[str] = None
    contact_id: Optional[int] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    unidade: Optional[str] = None
    procedimento: Optional[str] = None
    origem: Optional[str] = None
    suborigem: Optional[str] = None
    loss_reason: Optional[str] = None
    created_at: datetime
    closed_at: Optional[datetime] = None
    updated_at: datetime


class LeadListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[LeadResponse]

class CsvImportRowError(BaseModel):
    row_number: int
    error: str
    raw_data: Optional[Dict[str, Any]] = None

class CsvImportSummary(BaseModel):
    total_rows: int
    imported_count: int
    failed_count: int
    errors: List[CsvImportRowError] = []
