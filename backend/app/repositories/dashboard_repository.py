from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from app.models.domain import Lead, LeadStatus, Pipeline, User, Task, Event, LeadHistory

class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _build_lead_filter_query(
        self,
        period: str = "30days",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        consultora_id: Optional[int] = None,
        pipeline_id: Optional[int] = None,
        status_id: Optional[int] = None,
        unidade: Optional[str] = None,
        procedimento: Optional[str] = None,
        origem: Optional[str] = None,
        suborigem: Optional[str] = None,
        user_role: str = "Admin",
        current_user_id: Optional[int] = None,
    ):
        conditions = []

        # Period filtering
        now = datetime.utcnow()
        if period == "today":
            dt_start = datetime(now.year, now.month, now.day)
            conditions.append(Lead.created_at >= dt_start)
        elif period == "yesterday":
            dt_end = datetime(now.year, now.month, now.day)
            dt_start = dt_end - timedelta(days=1)
            conditions.append(and_(Lead.created_at >= dt_start, Lead.created_at < dt_end))
        elif period == "7days":
            conditions.append(Lead.created_at >= now - timedelta(days=7))
        elif period == "30days":
            conditions.append(Lead.created_at >= now - timedelta(days=30))
        elif period == "90days":
            conditions.append(Lead.created_at >= now - timedelta(days=90))
        elif period == "custom" and start_date and end_date:
            try:
                s_dt = datetime.fromisoformat(start_date)
                e_dt = datetime.fromisoformat(end_date)
                conditions.append(and_(Lead.created_at >= s_dt, Lead.created_at <= e_dt))
            except Exception:
                pass

        # Optional dropdown filters
        if consultora_id:
            conditions.append(Lead.responsible_user_id == consultora_id)
        if pipeline_id:
            conditions.append(Lead.pipeline_id == pipeline_id)
        if status_id:
            conditions.append(Lead.status_id == status_id)
        if unidade:
            conditions.append(Lead.unidade == unidade)
        if procedimento:
            conditions.append(Lead.procedimento == procedimento)
        if origem:
            conditions.append(Lead.origem == origem)
        if suborigem:
            conditions.append(Lead.suborigem == suborigem)

        # RBAC restriction for Consultora
        if user_role == "Consultora" and current_user_id:
            conditions.append(Lead.responsible_user_id == current_user_id)

        return conditions

    async def get_filtered_leads(self, **kwargs) -> List[Lead]:
        conditions = self._build_lead_filter_query(**kwargs)
        query = select(Lead).where(and_(*conditions)) if conditions else select(Lead)
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def get_performance_metrics(self, **kwargs) -> Dict[str, Any]:
        leads = await self.get_filtered_leads(**kwargs)
        total_leads = len(leads)
        if total_leads == 0:
            return {
                "avg_response_time_minutes": 0.0,
                "response_rate": 0.0,
                "active_leads": 0,
                "avg_sales_cycle_days": 0.0
            }

        response_times = [l.first_response_time_minutes for l in leads if l.first_response_time_minutes is not None]
        avg_response = (sum(response_times) / len(response_times)) if response_times else 0.0
        responded_count = len(response_times)
        response_rate = (responded_count / total_leads * 100.0) if total_leads > 0 else 0.0

        # Active leads: status is active (not won/lost status type 2 or 3)
        active_leads = len([l for l in leads if l.closed_at is None and l.loss_reason is None])

        sales_cycles = [l.sales_cycle_days for l in leads if l.sales_cycle_days is not None]
        avg_sales_cycle = (sum(sales_cycles) / len(sales_cycles)) if sales_cycles else 0.0

        return {
            "avg_response_time_minutes": round(avg_response, 1),
            "response_rate": round(response_rate, 1),
            "active_leads": active_leads,
            "avg_sales_cycle_days": round(avg_sales_cycle, 1)
        }

    async def get_ticket_metrics(self, **kwargs) -> Dict[str, Any]:
        leads = await self.get_filtered_leads(**kwargs)
        won_leads = [l for l in leads if l.price > 0 and (l.closed_at is not None or l.sales_cycle_days is not None) and not l.loss_reason]

        total_price = sum(l.price for l in won_leads)
        overall_ticket = (total_price / len(won_leads)) if won_leads else 0.0

        # By Procedure
        by_procedure_map: Dict[str, List[float]] = {}
        for l in won_leads:
            proc = l.procedimento or "Não Especificado"
            by_procedure_map.setdefault(proc, []).append(l.price)

        by_procedure = [
            {"procedimento": k, "ticket_medio": round(sum(v) / len(v), 2), "vendas": len(v)}
            for k, v in by_procedure_map.items()
        ]

        # By Unit
        by_unit_map: Dict[str, List[float]] = {}
        for l in won_leads:
            u = l.unidade or "Não Especificada"
            by_unit_map.setdefault(u, []).append(l.price)

        by_unit = [
            {"unidade": k, "ticket_medio": round(sum(v) / len(v), 2), "vendas": len(v)}
            for k, v in by_unit_map.items()
        ]

        return {
            "overall_ticket": round(overall_ticket, 2),
            "by_procedure": sorted(by_procedure, key=lambda x: x["ticket_medio"], reverse=True),
            "by_unit": sorted(by_unit, key=lambda x: x["ticket_medio"], reverse=True)
        }

    async def get_revenue_metrics(self, **kwargs) -> Dict[str, Any]:
        leads = await self.get_filtered_leads(**kwargs)
        won_leads = [l for l in leads if (l.closed_at is not None or l.sales_cycle_days is not None) and not l.loss_reason]

        total_revenue = sum(l.price for l in won_leads)
        total_sales = len(won_leads)

        # By Unit
        by_unit_map: Dict[str, float] = {}
        for l in won_leads:
            u = l.unidade or "Não Especificada"
            by_unit_map[u] = by_unit_map.get(u, 0.0) + l.price

        by_unit = [
            {"unidade": k, "receita": round(v, 2), "percentual": round((v / total_revenue * 100.0) if total_revenue > 0 else 0.0, 1)}
            for k, v in by_unit_map.items()
        ]

        # By Procedure
        by_procedure_map: Dict[str, float] = {}
        for l in won_leads:
            p = l.procedimento or "Não Especificado"
            by_procedure_map[p] = by_procedure_map.get(p, 0.0) + l.price

        by_procedure = [
            {"procedimento": k, "receita": round(v, 2), "percentual": round((v / total_revenue * 100.0) if total_revenue > 0 else 0.0, 1)}
            for k, v in by_procedure_map.items()
        ]

        return {
            "total_revenue": round(total_revenue, 2),
            "total_sales": total_sales,
            "by_unit": sorted(by_unit, key=lambda x: x["receita"], reverse=True),
            "by_procedure": sorted(by_procedure, key=lambda x: x["receita"], reverse=True)
        }

    async def get_funnel_performance(self, **kwargs) -> Dict[str, Any]:
        leads = await self.get_filtered_leads(**kwargs)
        total_leads = len(leads)

        # Query all statuses from DB
        status_res = await self.session.execute(select(LeadStatus).order_by(LeadStatus.sort_order.asc()))
        all_statuses = list(status_res.scalars().all())

        stages = []
        for s in all_statuses:
            stage_leads = [l for l in leads if l.status_id == s.id]
            cnt = len(stage_leads)
            pct = (cnt / total_leads * 100.0) if total_leads > 0 else 0.0
            
            # Conversion rate relative to total leads
            conv_rate = (cnt / total_leads * 100.0) if total_leads > 0 else 0.0
            losses_cnt = len([l for l in stage_leads if l.loss_reason])

            stages.append({
                "status_id": s.id,
                "name": s.name,
                "color": s.color or "#3b82f6",
                "quantity": cnt,
                "percentage": round(pct, 1),
                "conversion_rate": round(conv_rate, 1),
                "losses": losses_cnt
            })

        return {
            "total_leads": total_leads,
            "stages": stages
        }

    async def get_loss_metrics(self, **kwargs) -> Dict[str, Any]:
        leads = await self.get_filtered_leads(**kwargs)
        lost_leads = [l for l in leads if l.loss_reason is not None]
        total_lost_cnt = len(lost_leads)
        total_lost_val = sum(l.price for l in lost_leads)

        loss_map: Dict[str, Dict[str, Any]] = {}
        for l in lost_leads:
            reason = l.loss_reason or "Sem Motivo Declarado"
            if reason not in loss_map:
                loss_map[reason] = {"quantidade": 0, "valor_perdido": 0.0}
            loss_map[reason]["quantidade"] += 1
            loss_map[reason]["valor_perdido"] += l.price

        reasons = []
        for reason, data in loss_map.items():
            cnt = data["quantidade"]
            val = data["valor_perdido"]
            reasons.append({
                "motivo": reason,
                "quantidade": cnt,
                "percentual": round((cnt / total_lost_cnt * 100.0) if total_lost_cnt > 0 else 0.0, 1),
                "valor_perdido": round(val, 2)
            })

        return {
            "total_lost_count": total_lost_cnt,
            "total_lost_value": round(total_lost_val, 2),
            "reasons": sorted(reasons, key=lambda x: x["quantidade"], reverse=True)
        }

    async def get_ranking_metrics(self, **kwargs) -> Dict[str, Any]:
        leads = await self.get_filtered_leads(**kwargs)
        users_res = await self.session.execute(select(User))
        users = {u.id: u.name for u in users_res.scalars().all()}

        rep_map: Dict[int, Dict[str, Any]] = {}
        for l in leads:
            uid = l.responsible_user_id or 0
            if uid not in rep_map:
                rep_map[uid] = {
                    "user_id": uid,
                    "nome": users.get(uid, "Sem Responsável"),
                    "total_leads": 0,
                    "sales_count": 0,
                    "receita": 0.0,
                    "prices": []
                }
            rep_map[uid]["total_leads"] += 1
            is_won = (l.closed_at is not None or l.sales_cycle_days is not None) and not l.loss_reason
            if is_won:
                rep_map[uid]["sales_count"] += 1
                rep_map[uid]["receita"] += l.price
                rep_map[uid]["prices"].append(l.price)

        ranking = []
        for uid, data in rep_map.items():
            sales_cnt = data["sales_count"]
            tot_leads = data["total_leads"]
            rec = data["receita"]
            prices = data["prices"]
            ticket = (rec / sales_cnt) if sales_cnt > 0 else 0.0
            conv = (sales_cnt / tot_leads * 100.0) if tot_leads > 0 else 0.0

            ranking.append({
                "user_id": uid,
                "nome": data["nome"],
                "receita": round(rec, 2),
                "vendas": sales_cnt,
                "ticket_medio": round(ticket, 2),
                "conversao": round(conv, 1)
            })

        return {
            "ranking": sorted(ranking, key=lambda x: x["receita"], reverse=True)
        }

    async def get_followup_metrics(self, **kwargs) -> Dict[str, Any]:
        now = datetime.utcnow()
        tasks_res = await self.session.execute(select(Task))
        tasks = list(tasks_res.scalars().all())

        users_res = await self.session.execute(select(User))
        users = {u.id: u.name for u in users_res.scalars().all()}

        overdue_tasks = [t for t in tasks if not t.is_completed and t.due_date and t.due_date < now]
        open_tasks = [t for t in tasks if not t.is_completed]
        completed_tasks = [t for t in tasks if t.is_completed]

        resolution_times = [t.resolution_time_hours for t in completed_tasks if t.resolution_time_hours is not None]
        avg_res_time = (sum(resolution_times) / len(resolution_times)) if resolution_times else 0.0

        by_user_map: Dict[int, Dict[str, Any]] = {}
        for t in tasks:
            uid = t.responsible_user_id or 0
            if uid not in by_user_map:
                by_user_map[uid] = {"nome": users.get(uid, "Outro"), "atrasadas": 0, "abertas": 0, "concluidas": 0}
            if t.is_completed:
                by_user_map[uid]["concluidas"] += 1
            else:
                by_user_map[uid]["abertas"] += 1
                if t.due_date and t.due_date < now:
                    by_user_map[uid]["atrasadas"] += 1

        by_employee = [
            {"user_id": uid, **val} for uid, val in by_user_map.items()
        ]

        return {
            "overdue_count": len(overdue_tasks),
            "open_count": len(open_tasks),
            "completed_count": len(completed_tasks),
            "avg_resolution_time_hours": round(avg_res_time, 1),
            "by_employee": sorted(by_employee, key=lambda x: x["abertas"], reverse=True)
        }

    async def get_origins_metrics(self, **kwargs) -> Dict[str, Any]:
        leads = await self.get_filtered_leads(**kwargs)

        # Sales & Revenue & Conversion by Source
        orig_map: Dict[str, Dict[str, Any]] = {}
        suborig_map: Dict[str, Dict[str, Any]] = {}

        for l in leads:
            orig = l.origem or "Outros"
            suborig = l.suborigem or "Outros"
            is_won = (l.closed_at is not None or l.sales_cycle_days is not None) and not l.loss_reason

            if orig not in orig_map:
                orig_map[orig] = {"leads": 0, "vendas": 0, "receita": 0.0}
            orig_map[orig]["leads"] += 1
            if is_won:
                orig_map[orig]["vendas"] += 1
                orig_map[orig]["receita"] += l.price

            if suborig not in suborig_map:
                suborig_map[suborig] = {"leads": 0, "vendas": 0, "receita": 0.0}
            suborig_map[suborig]["leads"] += 1
            if is_won:
                suborig_map[suborig]["vendas"] += 1
                suborig_map[suborig]["receita"] += l.price

        vendas_por_origem = [
            {
                "origem": k,
                "vendas": v["vendas"],
                "receita": round(v["receita"], 2),
                "conversao": round((v["vendas"] / v["leads"] * 100.0) if v["leads"] > 0 else 0.0, 1)
            }
            for k, v in orig_map.items()
        ]

        vendas_por_suborigem = [
            {
                "suborigem": k,
                "vendas": v["vendas"],
                "receita": round(v["receita"], 2),
                "conversao": round((v["vendas"] / v["leads"] * 100.0) if v["leads"] > 0 else 0.0, 1)
            }
            for k, v in suborig_map.items()
        ]

        return {
            "by_origin": sorted(vendas_por_origem, key=lambda x: x["receita"], reverse=True),
            "by_suborigin": sorted(vendas_por_suborigem, key=lambda x: x["receita"], reverse=True)
        }
