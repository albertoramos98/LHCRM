from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class FilterParams(BaseModel):
    period: str = "30days" # today, yesterday, 7days, 30days, 90days, custom
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    consultora_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    status_id: Optional[int] = None
    unidade: Optional[str] = None
    procedimento: Optional[str] = None
    origem: Optional[str] = None
    suborigem: Optional[str] = None
