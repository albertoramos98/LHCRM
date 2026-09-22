from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from app.models.domain import MacroMetric, User
from app.schemas.goals import GoalCreate, GoalUpdate, GoalResponse, GoalSummaryResponse
from app.repositories.dashboard_repository import DashboardRepository

class GoalService:
    def __init__(self, session: AsyncSession, organization_id: int):
        self.session = session
        self.organization_id = organization_id
        self.dashboard_repo = DashboardRepository(session, organization_id)

    async def create_or_update_goal(self, data: GoalCreate) -> GoalResponse:
        # Check if an entry exists for (organization_id, period_month, consultora_id)
        q = select(MacroMetric).where(
            MacroMetric.organization_id == self.organization_id,
            MacroMetric.period_month == data.period_month
        )
        if data.consultora_id:
            q = q.where(MacroMetric.consultora_id == data.consultora_id)
        else:
            q = q.where(MacroMetric.consultora_id.is_(None))

        res = await self.session.execute(q)
        goal = res.scalars().first()

        if goal:
            goal.revenue_target = data.revenue_target
            goal.leads_target = data.leads_target
            goal.sales_target = data.sales_target
            goal.marketing_investment = data.marketing_investment
            goal.fixed_costs = data.fixed_costs
            goal.notes = data.notes
            goal.updated_at = datetime.now(timezone.utc)
        else:
            goal = MacroMetric(
                organization_id=self.organization_id,
                period_month=data.period_month,
                consultora_id=data.consultora_id,
                revenue_target=data.revenue_target,
                leads_target=data.leads_target,
                sales_target=data.sales_target,
                marketing_investment=data.marketing_investment,
                fixed_costs=data.fixed_costs,
                notes=data.notes,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.session.add(goal)

        await self.session.commit()
        await self.session.refresh(goal)

        # Get consultora name
        consultora_name = None
        if goal.consultora_id:
            u_res = await self.session.execute(select(User.name).where(User.id == goal.consultora_id))
            consultora_name = u_res.scalar_one_or_none()

        return GoalResponse(
            id=goal.id,
            organization_id=goal.organization_id,
            period_month=goal.period_month,
            consultora_id=goal.consultora_id,
            consultora_name=consultora_name or "Global Empresa",
            revenue_target=goal.revenue_target,
            leads_target=goal.leads_target,
            sales_target=goal.sales_target,
            marketing_investment=goal.marketing_investment,
            fixed_costs=goal.fixed_costs,
            notes=goal.notes,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )

    async def list_goals(self, period_month: Optional[str] = None) -> List[GoalResponse]:
        q = select(MacroMetric).where(MacroMetric.organization_id == self.organization_id)
        if period_month:
            q = q.where(MacroMetric.period_month == period_month)
        q = q.order_by(MacroMetric.period_month.desc(), MacroMetric.id)

        res = await self.session.execute(q)
        goals = list(res.scalars().all())

        user_ids = [g.consultora_id for g in goals if g.consultora_id]
        user_names = {}
        if user_ids:
            u_res = await self.session.execute(select(User.id, User.name).where(User.id.in_(user_ids)))
            user_names = {u[0]: u[1] for u in u_res.all()}

        return [
            GoalResponse(
                id=g.id,
                organization_id=g.organization_id,
                period_month=g.period_month,
                consultora_id=g.consultora_id,
                consultora_name=user_names.get(g.consultora_id) if g.consultora_id else "Global Empresa",
                revenue_target=g.revenue_target,
                leads_target=g.leads_target,
                sales_target=g.sales_target,
                marketing_investment=g.marketing_investment,
                fixed_costs=g.fixed_costs,
                notes=g.notes,
                created_at=g.created_at,
                updated_at=g.updated_at
            )
            for g in goals
        ]

    async def delete_goal(self, goal_id: int) -> bool:
        q = select(MacroMetric).where(
            MacroMetric.id == goal_id,
            MacroMetric.organization_id == self.organization_id
        )
        res = await self.session.execute(q)
        goal = res.scalars().first()
        if not goal:
            return False

        await self.session.delete(goal)
        await self.session.commit()
        return True

    async def get_summary(self, period_month: str, consultora_id: Optional[int] = None) -> GoalSummaryResponse:
        raw_summary = await self.dashboard_repo.get_goals_and_cac_metrics(
            period_month=period_month,
            consultora_id=consultora_id
        )
        return GoalSummaryResponse(**raw_summary)
