import json
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.dashboard_repository import DashboardRepository
from app.core.cache import memory_cache

class DashboardService:
    def __init__(self, session: AsyncSession):
        self.repository = DashboardRepository(session)

    def _make_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        # Sort keys for consistent cache key generation
        serialized = json.dumps(params, sort_keys=True, default=str)
        return f"{prefix}:{serialized}"

    async def get_overview(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("overview", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        revenue = await self.repository.get_revenue_metrics(**params)
        performance = await self.repository.get_performance_metrics(**params)
        tickets = await self.repository.get_ticket_metrics(**params)

        res = {
            "total_revenue": revenue["total_revenue"],
            "total_sales": revenue["total_sales"],
            "overall_ticket": tickets["overall_ticket"],
            "avg_response_time_minutes": performance["avg_response_time_minutes"],
            "response_rate": performance["response_rate"],
            "active_leads": performance["active_leads"],
            "avg_sales_cycle_days": performance["avg_sales_cycle_days"]
        }
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_funnel(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("funnel", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = await self.repository.get_funnel_performance(**params)
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_revenue(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("revenue", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = await self.repository.get_revenue_metrics(**params)
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_followup(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("followup", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = await self.repository.get_followup_metrics(**params)
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_ranking(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("ranking", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = await self.repository.get_ranking_metrics(**params)
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_losses(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("losses", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = await self.repository.get_loss_metrics(**params)
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_origins(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("origins", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = await self.repository.get_origins_metrics(**params)
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_tickets(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("tickets", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = await self.repository.get_ticket_metrics(**params)
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_performance(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("performance", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = await self.repository.get_performance_metrics(**params)
        memory_cache.set(key, res, ttl=60)
        return res

    async def get_all_metrics(self, **params) -> Dict[str, Any]:
        key = self._make_cache_key("all_metrics", params)
        cached = memory_cache.get(key)
        if cached:
            return cached

        res = {
            "overview": await self.get_overview(**params),
            "funnel": await self.get_funnel(**params),
            "revenue": await self.get_revenue(**params),
            "followup": await self.get_followup(**params),
            "ranking": await self.get_ranking(**params),
            "losses": await self.get_losses(**params),
            "origins": await self.get_origins(**params),
            "tickets": await self.get_tickets(**params),
            "performance": await self.get_performance(**params),
        }
        memory_cache.set(key, res, ttl=60)
        return res
