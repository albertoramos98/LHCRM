from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.domain import (
    User, Contact, Company, Pipeline, LeadStatus, Lead, Task, Event,
    CustomField, Tag, SyncLog, LeadHistory
)

class SyncRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_sync_log(self, trigger_type: str = "automatic") -> SyncLog:
        log = SyncLog(
            started_at=datetime.utcnow(),
            trigger_type=trigger_type,
            status="in_progress",
            items_synced=0
        )
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log

    async def finish_sync_log(self, log_id: int, status: str, items_synced: int, error_message: Optional[str] = None):
        stmt = (
            update(SyncLog)
            .where(SyncLog.id == log_id)
            .values(
                finished_at=datetime.utcnow(),
                status=status,
                items_synced=items_synced,
                error_message=error_message
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_latest_sync_log(self) -> Optional[SyncLog]:
        res = await self.session.execute(
            select(SyncLog).order_by(SyncLog.id.desc()).limit(1)
        )
        return res.scalar_one_or_none()

    async def upsert_users(self, users_data: List[Dict[str, Any]]) -> int:
        count = 0
        for u in users_data:
            ext_id = u.get("id")
            name = u.get("name") or "User"
            email = u.get("email") or f"user_{ext_id}@crm.com"
            role = u.get("role") or "Consultora"

            res = await self.session.execute(select(User).where(User.external_id == ext_id))
            user = res.scalar_one_or_none()
            if user:
                user.name = name
                user.email = email
                user.role = role
            else:
                user = User(
                    external_id=ext_id,
                    name=name,
                    email=email,
                    role=role
                )
                self.session.add(user)
            count += 1
        await self.session.commit()
        return count

    async def upsert_pipelines_and_statuses(self, pipelines_data: List[Dict[str, Any]]) -> int:
        count = 0
        for p in pipelines_data:
            p_ext_id = p.get("id")
            p_name = p.get("name") or "Pipeline"
            is_main = p.get("is_main", False)

            res = await self.session.execute(select(Pipeline).where(Pipeline.external_id == p_ext_id))
            pipeline = res.scalar_one_or_none()
            if pipeline:
                pipeline.name = p_name
                pipeline.is_main = is_main
            else:
                pipeline = Pipeline(external_id=p_ext_id, name=p_name, is_main=is_main)
                self.session.add(pipeline)
                await self.session.flush()

            statuses = p.get("_embedded", {}).get("statuses", []) or p.get("statuses", [])
            for s in statuses:
                s_ext_id = s.get("id")
                s_name = s.get("name") or "Status"
                sort_order = s.get("sort", 0)
                color = s.get("color")
                s_type = s.get("type", 1)

                s_res = await self.session.execute(select(LeadStatus).where(LeadStatus.external_id == s_ext_id))
                status_obj = s_res.scalar_one_or_none()
                if status_obj:
                    status_obj.name = s_name
                    status_obj.sort_order = sort_order
                    status_obj.color = color
                    status_obj.type = s_type
                    status_obj.pipeline_id = pipeline.id
                else:
                    status_obj = LeadStatus(
                        external_id=s_ext_id,
                        pipeline_id=pipeline.id,
                        name=s_name,
                        sort_order=sort_order,
                        color=color,
                        type=s_type
                    )
                    self.session.add(status_obj)
            count += 1
        await self.session.commit()
        return count

    async def upsert_contacts(self, contacts_data: List[Dict[str, Any]]) -> int:
        count = 0
        for c in contacts_data:
            ext_id = c.get("id")
            name = c.get("name") or "Contact"
            phone = c.get("phone")
            email = c.get("email")

            res = await self.session.execute(select(Contact).where(Contact.external_id == ext_id))
            contact = res.scalar_one_or_none()
            if contact:
                contact.name = name
                contact.phone = phone
                contact.email = email
            else:
                contact = Contact(
                    external_id=ext_id,
                    name=name,
                    phone=phone,
                    email=email
                )
                self.session.add(contact)
            count += 1
        await self.session.commit()
        return count

    async def upsert_companies(self, companies_data: List[Dict[str, Any]]) -> int:
        count = 0
        for comp in companies_data:
            ext_id = comp.get("id")
            name = comp.get("name") or "Company"

            res = await self.session.execute(select(Company).where(Company.external_id == ext_id))
            company = res.scalar_one_or_none()
            if company:
                company.name = name
            else:
                company = Company(external_id=ext_id, name=name)
                self.session.add(company)
            count += 1
        await self.session.commit()
        return count

    async def upsert_leads(self, leads_data: List[Dict[str, Any]]) -> int:
        count = 0
        for ld in leads_data:
            ext_id = ld.get("id")
            name = ld.get("name") or f"Lead #{ext_id}"
            price = float(ld.get("price") or 0.0)

            # Map external user_id to internal DB user id
            resp_ext_user_id = ld.get("responsible_user_id")
            resp_user_id = None
            if resp_ext_user_id:
                u_res = await self.session.execute(select(User.id).where(User.external_id == resp_ext_user_id))
                resp_user_id = u_res.scalar_one_or_none()

            # Map pipeline & status
            p_ext_id = ld.get("pipeline_id")
            s_ext_id = ld.get("status_id")

            p_res = await self.session.execute(select(Pipeline.id).where(Pipeline.external_id == p_ext_id))
            pipeline_id = p_res.scalar_one_or_none() or 1

            s_res = await self.session.execute(select(LeadStatus.id).where(LeadStatus.external_id == s_ext_id))
            status_id = s_res.scalar_one_or_none() or 10

            contact_ext_id = ld.get("contact_id")
            contact_id = None
            if contact_ext_id:
                c_res = await self.session.execute(select(Contact.id).where(Contact.external_id == contact_ext_id))
                contact_id = c_res.scalar_one_or_none()

            company_ext_id = ld.get("company_id")
            company_id = None
            if company_ext_id:
                comp_res = await self.session.execute(select(Company.id).where(Company.external_id == company_ext_id))
                company_id = comp_res.scalar_one_or_none()

            created_at_val = datetime.fromisoformat(ld["created_at"]) if isinstance(ld.get("created_at"), str) else datetime.utcnow()
            closed_at_val = datetime.fromisoformat(ld["closed_at"]) if isinstance(ld.get("closed_at"), str) else None

            res = await self.session.execute(select(Lead).where(Lead.external_id == ext_id))
            lead = res.scalar_one_or_none()

            old_status_id = lead.status_id if lead else None

            if lead:
                lead.name = name
                lead.price = price
                lead.pipeline_id = pipeline_id
                lead.status_id = status_id
                lead.responsible_user_id = resp_user_id
                lead.contact_id = contact_id
                lead.company_id = company_id
                lead.unidade = ld.get("unidade")
                lead.procedimento = ld.get("procedimento")
                lead.origem = ld.get("origem")
                lead.suborigem = ld.get("suborigem")
                lead.loss_reason = ld.get("loss_reason")
                lead.first_response_time_minutes = ld.get("first_response_time_minutes")
                lead.sales_cycle_days = ld.get("sales_cycle_days")
                lead.closed_at = closed_at_val
            else:
                lead = Lead(
                    external_id=ext_id,
                    name=name,
                    price=price,
                    pipeline_id=pipeline_id,
                    status_id=status_id,
                    responsible_user_id=resp_user_id,
                    contact_id=contact_id,
                    company_id=company_id,
                    unidade=ld.get("unidade"),
                    procedimento=ld.get("procedimento"),
                    origem=ld.get("origem"),
                    suborigem=ld.get("suborigem"),
                    loss_reason=ld.get("loss_reason"),
                    first_response_time_minutes=ld.get("first_response_time_minutes"),
                    sales_cycle_days=ld.get("sales_cycle_days"),
                    created_at=created_at_val,
                    closed_at=closed_at_val,
                )
                self.session.add(lead)
                await self.session.flush()

            # Record history if status changed
            if old_status_id != status_id:
                history = LeadHistory(
                    lead_id=lead.id,
                    from_status_id=old_status_id,
                    to_status_id=status_id,
                    changed_at=datetime.utcnow()
                )
                self.session.add(history)

            count += 1
        await self.session.commit()
        return count

    async def upsert_tasks(self, tasks_data: List[Dict[str, Any]]) -> int:
        count = 0
        for t in tasks_data:
            ext_id = t.get("id")
            text = t.get("text") or "Task"
            is_completed = bool(t.get("is_completed"))

            lead_ext_id = t.get("lead_id")
            lead_id = None
            if lead_ext_id:
                l_res = await self.session.execute(select(Lead.id).where(Lead.external_id == lead_ext_id))
                lead_id = l_res.scalar_one_or_none()

            resp_ext_user_id = t.get("responsible_user_id")
            resp_user_id = None
            if resp_ext_user_id:
                u_res = await self.session.execute(select(User.id).where(User.external_id == resp_ext_user_id))
                resp_user_id = u_res.scalar_one_or_none()

            due_date_val = datetime.fromisoformat(t["due_date"]) if isinstance(t.get("due_date"), str) else None
            completed_at_val = datetime.fromisoformat(t["completed_at"]) if isinstance(t.get("completed_at"), str) else None

            res = await self.session.execute(select(Task).where(Task.external_id == ext_id))
            task = res.scalar_one_or_none()
            if task:
                task.text = text
                task.is_completed = is_completed
                task.lead_id = lead_id
                task.responsible_user_id = resp_user_id
                task.due_date = due_date_val
                task.completed_at = completed_at_val
                task.resolution_time_hours = t.get("resolution_time_hours")
            else:
                task = Task(
                    external_id=ext_id,
                    text=text,
                    is_completed=is_completed,
                    lead_id=lead_id,
                    responsible_user_id=resp_user_id,
                    due_date=due_date_val,
                    completed_at=completed_at_val,
                    resolution_time_hours=t.get("resolution_time_hours")
                )
                self.session.add(task)
            count += 1
        await self.session.commit()
        return count

    async def upsert_events(self, events_data: List[Dict[str, Any]]) -> int:
        count = 0
        for ev in events_data:
            ext_id = str(ev.get("id"))
            ev_type = ev.get("type") or "general"
            lead_ext_id = ev.get("lead_id")
            lead_id = None
            if lead_ext_id:
                l_res = await self.session.execute(select(Lead.id).where(Lead.external_id == lead_ext_id))
                lead_id = l_res.scalar_one_or_none()

            res = await self.session.execute(select(Event).where(Event.external_id == ext_id))
            event = res.scalar_one_or_none()
            if not event:
                event = Event(
                    external_id=ext_id,
                    lead_id=lead_id,
                    type=ev_type,
                    value_before=ev.get("value_before"),
                    value_after=ev.get("value_after")
                )
                self.session.add(event)
                count += 1
        await self.session.commit()
        return count

    async def upsert_custom_fields(self, fields_data: List[Dict[str, Any]]) -> int:
        count = 0
        for cf in fields_data:
            ext_id = cf.get("id")
            name = cf.get("name") or "Field"
            code = cf.get("code")
            f_type = cf.get("type") or "text"

            res = await self.session.execute(select(CustomField).where(CustomField.external_id == ext_id))
            field = res.scalar_one_or_none()
            if field:
                field.name = name
                field.code = code
                field.field_type = f_type
            else:
                field = CustomField(external_id=ext_id, name=name, code=code, field_type=f_type)
                self.session.add(field)
            count += 1
        await self.session.commit()
        return count

    async def upsert_tags(self, tags_data: List[Dict[str, Any]]) -> int:
        count = 0
        for tg in tags_data:
            ext_id = tg.get("id")
            name = tg.get("name") or "Tag"
            color = tg.get("color")

            res = await self.session.execute(select(Tag).where(Tag.external_id == ext_id))
            tag = res.scalar_one_or_none()
            if tag:
                tag.name = name
                tag.color = color
            else:
                tag = Tag(external_id=ext_id, name=name, color=color)
                self.session.add(tag)
            count += 1
        await self.session.commit()
        return count
