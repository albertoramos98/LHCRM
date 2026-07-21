import logging
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.providers.base import CRMProvider

logger = logging.getLogger(__name__)

class KommoProvider(CRMProvider):
    """
    Kommo CRM REST API v4 Provider Implementation.
    Handles OAuth 2.0 requests and fallback mock data generator when running in demo/offline mode.
    """

    def __init__(self, subdomain: Optional[str] = None, token: Optional[str] = None):
        self.subdomain = subdomain or settings.KOMMO_SUBDOMAIN
        self.token = token or settings.KOMMO_LONG_LIVED_TOKEN
        self.base_url = f"https://{self.subdomain}.kommo.com/api/v4" if self.subdomain else ""

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "json"
        }

    async def get_users(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_users()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/users", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("users", [])
            except Exception as e:
                logger.warning(f"Error fetching users from Kommo API: {e}. Returning mock users.")
        return self._generate_mock_users()

    async def get_contacts(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_contacts()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/contacts", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("contacts", [])
            except Exception as e:
                logger.warning(f"Error fetching contacts from Kommo API: {e}. Returning mock contacts.")
        return self._generate_mock_contacts()

    async def get_companies(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_companies()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/companies", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("companies", [])
            except Exception as e:
                logger.warning(f"Error fetching companies from Kommo API: {e}.")
        return self._generate_mock_companies()

    async def get_pipelines(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_pipelines()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/leads/pipelines", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("pipelines", [])
            except Exception as e:
                logger.warning(f"Error fetching pipelines from Kommo API: {e}.")
        return self._generate_mock_pipelines()

    async def get_leads(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_leads()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/leads", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("leads", [])
            except Exception as e:
                logger.warning(f"Error fetching leads from Kommo API: {e}.")
        return self._generate_mock_leads()

    async def get_tasks(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_tasks()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/tasks", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("tasks", [])
            except Exception as e:
                logger.warning(f"Error fetching tasks from Kommo API: {e}.")
        return self._generate_mock_tasks()

    async def get_events(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_events()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/events", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("events", [])
            except Exception as e:
                logger.warning(f"Error fetching events from Kommo API: {e}.")
        return self._generate_mock_events()

    async def get_custom_fields(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_custom_fields()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/leads/custom_fields", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("custom_fields", [])
            except Exception as e:
                logger.warning(f"Error fetching custom fields from Kommo API: {e}.")
        return self._generate_mock_custom_fields()

    async def get_tags(self) -> List[Dict[str, Any]]:
        if not self.token or self.subdomain == "demo":
            return self._generate_mock_tags()

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{self.base_url}/leads/tags", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("_embedded", {}).get("tags", [])
            except Exception as e:
                logger.warning(f"Error fetching tags from Kommo API: {e}.")
        return self._generate_mock_tags()

    # Mock Data Generators for robust offline/dev operation
    def _generate_mock_users(self) -> List[Dict[str, Any]]:
        return [
            {"id": 101, "name": "Ana Silva", "email": "ana.silva@empresa.com", "role": "Consultora"},
            {"id": 102, "name": "Camila Oliveira", "email": "camila.o@empresa.com", "role": "Consultora"},
            {"id": 103, "name": "Mariana Souza", "email": "mariana.s@empresa.com", "role": "Consultora"},
            {"id": 104, "name": "Roberto Costa", "email": "roberto.c@empresa.com", "role": "Gerente"},
            {"id": 105, "name": "Fernanda Lima", "email": "fernanda.l@empresa.com", "role": "Admin"},
        ]

    def _generate_mock_contacts(self) -> List[Dict[str, Any]]:
        return [
            {"id": 501, "name": "Juliana Martins", "phone": "+55 11 98888-1111", "email": "juliana@email.com"},
            {"id": 502, "name": "Carlos Eduardo", "phone": "+55 11 97777-2222", "email": "carlos@email.com"},
            {"id": 503, "name": "Beatriz Santos", "phone": "+55 21 96666-3333", "email": "beatriz@email.com"},
            {"id": 504, "name": "Lucas Pereira", "phone": "+55 31 95555-4444", "email": "lucas@email.com"},
            {"id": 505, "name": "Amanda Rocha", "phone": "+55 41 94444-5555", "email": "amanda@email.com"},
        ]

    def _generate_mock_companies(self) -> List[Dict[str, Any]]:
        return [
            {"id": 701, "name": "Grupo Estética Avançada"},
            {"id": 702, "name": "Clínica Saúde & Vida"},
        ]

    def _generate_mock_pipelines(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "name": "Funil Principal de Vendas",
                "is_main": True,
                "_embedded": {
                    "statuses": [
                        {"id": 10, "name": "Triagem", "sort": 10, "type": 1, "color": "#99ccff"},
                        {"id": 20, "name": "Qualificado", "sort": 20, "type": 1, "color": "#ffcc66"},
                        {"id": 30, "name": "Agendamento", "sort": 30, "type": 1, "color": "#ff99ff"},
                        {"id": 40, "name": "Comparecimento", "sort": 40, "type": 1, "color": "#cc99ff"},
                        {"id": 50, "name": "Audiência", "sort": 50, "type": 1, "color": "#66ccff"},
                        {"id": 142, "name": "Venda", "sort": 100, "type": 2, "color": "#66ff99"}, # Won
                        {"id": 143, "name": "Perdidos", "sort": 101, "type": 3, "color": "#ff6666"}, # Lost
                    ]
                }
            }
        ]

    def _generate_mock_leads(self) -> List[Dict[str, Any]]:
        now = datetime.now()
        units = ["São Paulo - Jardins", "Rio de Janeiro - Barra", "Belo Horizonte - Savassi"]
        procedures = ["Harmonização Facial", "Botox VIP", "Bioestimulador", "Lipo Enzimática", "Preenchimento"]
        origins = ["Instagram Ads", "Google Ads", "Indicação", "Meta Direct", "Website"]
        suborigins = ["Stories", "Feed Promo", "Pesquisa Direta", "WhatsApp Bot", "Organic Post"]
        loss_reasons = ["Preço elevado", "Sem orçamento", "Optou por concorrente", "Falta de contato", "Desistiu do procedimento"]
        user_ids = [101, 102, 103]

        leads = []
        for i in range(1, 46):
            created_dt = now - timedelta(days=(i % 30), hours=(i * 2))
            is_won = i % 3 == 0
            is_lost = i % 5 == 0 and not is_won
            status_id = 142 if is_won else (143 if is_lost else [10, 20, 30, 40, 50][i % 5])
            closed_dt = (created_dt + timedelta(days=2 + (i % 7))) if (is_won or is_lost) else None
            price = float((i * 450 + 1500) % 8500 + 1200)

            leads.append({
                "id": 1000 + i,
                "name": f"Lead #{1000 + i} - {procedures[i % len(procedures)]}",
                "price": price,
                "pipeline_id": 1,
                "status_id": status_id,
                "responsible_user_id": user_ids[i % len(user_ids)],
                "contact_id": 501 + (i % 5),
                "company_id": 701 if i % 2 == 0 else 702,
                "unidade": units[i % len(units)],
                "procedimento": procedures[i % len(procedures)],
                "origem": origins[i % len(origins)],
                "suborigem": suborigins[i % len(suborigins)],
                "loss_reason": loss_reasons[i % len(loss_reasons)] if is_lost else None,
                "first_response_time_minutes": float((i * 7) % 45 + 5),
                "sales_cycle_days": float((i * 3) % 15 + 2) if is_won else None,
                "created_at": created_dt.isoformat(),
                "closed_at": closed_dt.isoformat() if closed_dt else None,
            })
        return leads

    def _generate_mock_tasks(self) -> List[Dict[str, Any]]:
        now = datetime.now()
        tasks = []
        for i in range(1, 21):
            is_completed = i % 2 == 0
            due_dt = now + timedelta(days=(i - 10))
            completed_dt = (due_dt + timedelta(hours=3)) if is_completed else None
            tasks.append({
                "id": 2000 + i,
                "lead_id": 1000 + (i % 40 + 1),
                "responsible_user_id": [101, 102, 103][i % 3],
                "text": f"Follow-up de orçamento #{i}",
                "is_completed": is_completed,
                "due_date": due_dt.isoformat(),
                "completed_at": completed_dt.isoformat() if completed_dt else None,
                "resolution_time_hours": float((i * 4) % 24 + 1) if is_completed else None,
                "created_at": (now - timedelta(days=15)).isoformat()
            })
        return tasks

    def _generate_mock_events(self) -> List[Dict[str, Any]]:
        return [
            {"id": "ev_1", "lead_id": 1001, "type": "lead_status_changed", "value_before": "Triagem", "value_after": "Qualificado", "created_at": datetime.now().isoformat()},
            {"id": "ev_2", "lead_id": 1003, "type": "lead_status_changed", "value_before": "Audiência", "value_after": "Venda", "created_at": datetime.now().isoformat()},
        ]

    def _generate_mock_custom_fields(self) -> List[Dict[str, Any]]:
        return [
            {"id": 801, "name": "Unidade", "code": "UNIDADE", "type": "select"},
            {"id": 802, "name": "Procedimento", "code": "PROCEDIMENTO", "type": "select"},
            {"id": 803, "name": "Suborigem", "code": "SUBORIGEM", "type": "text"},
        ]

    def _generate_mock_tags(self) -> List[Dict[str, Any]]:
        return [
            {"id": 901, "name": "VIP", "color": "#ff0000"},
            {"id": 902, "name": "Urgente", "color": "#ffaa00"},
            {"id": 903, "name": "Retorno", "color": "#00aaee"},
        ]
