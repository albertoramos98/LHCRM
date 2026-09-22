import io
import csv
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.domain import Lead, LeadStatus, Pipeline, User, Contact, Company, LeadHistory
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse, CsvImportSummary, CsvImportRowError

class LeadService:
    def __init__(self, session: AsyncSession, organization_id: int):
        self.session = session
        self.organization_id = organization_id

    async def _get_or_create_default_pipeline(self) -> tuple[int, int]:
        """Finds or creates a default pipeline and initial status for the organization."""
        pipe_res = await self.session.execute(
            select(Pipeline).where(Pipeline.organization_id == self.organization_id).order_by(Pipeline.id)
        )
        pipe = pipe_res.scalars().first()
        if not pipe:
            pipe = Pipeline(
                organization_id=self.organization_id,
                name="Funil de Vendas",
                is_main=True
            )
            self.session.add(pipe)
            await self.session.flush()

        status_res = await self.session.execute(
            select(LeadStatus).where(
                LeadStatus.organization_id == self.organization_id,
                LeadStatus.pipeline_id == pipe.id
            ).order_by(LeadStatus.sort_order, LeadStatus.id)
        )
        status = status_res.scalars().first()
        if not status:
            status = LeadStatus(
                organization_id=self.organization_id,
                pipeline_id=pipe.id,
                name="Novo Lead",
                sort_order=1,
                type=1
            )
            self.session.add(status)
            await self.session.flush()

        return pipe.id, status.id

    async def create_lead(self, data: LeadCreate, current_user_id: Optional[int] = None) -> LeadResponse:
        # Resolve pipeline and status
        pipe_id = data.pipeline_id
        status_id = data.status_id

        if not pipe_id or not status_id:
            def_pipe, def_status = await self._get_or_create_default_pipeline()
            pipe_id = pipe_id or def_pipe
            status_id = status_id or def_status

        # Create or link contact if contact information provided
        contact_id = None
        if data.contact_name or data.contact_phone or data.contact_email:
            contact = Contact(
                organization_id=self.organization_id,
                name=data.contact_name or data.name,
                phone=data.contact_phone,
                email=data.contact_email
            )
            self.session.add(contact)
            await self.session.flush()
            contact_id = contact.id

        # Determine responsible user
        resp_user_id = data.responsible_user_id or current_user_id

        # Check if status is a won status
        status_res = await self.session.execute(
            select(LeadStatus).where(LeadStatus.id == status_id)
        )
        status_obj = status_res.scalars().first()
        closed_at = None
        if status_obj and (status_obj.type == 2 or "ganh" in status_obj.name.lower() or "vend" in status_obj.name.lower() or "fechad" in status_obj.name.lower()):
            closed_at = datetime.now(timezone.utc)

        lead = Lead(
            organization_id=self.organization_id,
            name=data.name,
            price=data.price,
            pipeline_id=pipe_id,
            status_id=status_id,
            responsible_user_id=resp_user_id,
            contact_id=contact_id,
            source_type=data.source_type or "manual",
            unidade=data.unidade,
            procedimento=data.procedimento,
            origem=data.origem or "Manual",
            suborigem=data.suborigem,
            loss_reason=data.loss_reason,
            custom_fields_values=data.custom_fields_values,
            created_at=datetime.now(timezone.utc),
            closed_at=closed_at,
            updated_at=datetime.now(timezone.utc)
        )
        self.session.add(lead)
        await self.session.flush()

        # Record initial history
        history = LeadHistory(
            organization_id=self.organization_id,
            lead_id=lead.id,
            to_status_id=status_id,
            changed_at=datetime.now(timezone.utc)
        )
        self.session.add(history)
        await self.session.commit()
        await self.session.refresh(lead)

        return await self.get_lead(lead.id)

    async def get_lead(self, lead_id: int) -> Optional[LeadResponse]:
        query = select(Lead).where(
            Lead.id == lead_id,
            Lead.organization_id == self.organization_id
        )
        res = await self.session.execute(query)
        lead = res.scalars().first()
        if not lead:
            return None

        # Fetch extra relation names
        pipe_name, status_name, user_name, contact_name, contact_phone, contact_email = None, None, None, None, None, None
        
        if lead.pipeline_id:
            p_res = await self.session.execute(select(Pipeline.name).where(Pipeline.id == lead.pipeline_id))
            pipe_name = p_res.scalar_one_or_none()
        if lead.status_id:
            s_res = await self.session.execute(select(LeadStatus.name).where(LeadStatus.id == lead.status_id))
            status_name = s_res.scalar_one_or_none()
        if lead.responsible_user_id:
            u_res = await self.session.execute(select(User.name).where(User.id == lead.responsible_user_id))
            user_name = u_res.scalar_one_or_none()
        if lead.contact_id:
            c_res = await self.session.execute(select(Contact).where(Contact.id == lead.contact_id))
            c = c_res.scalars().first()
            if c:
                contact_name = c.name
                contact_phone = c.phone
                contact_email = c.email

        return LeadResponse(
            id=lead.id,
            organization_id=lead.organization_id,
            external_id=lead.external_id,
            source_type=lead.source_type or "kommo",
            name=lead.name,
            price=lead.price,
            pipeline_id=lead.pipeline_id,
            pipeline_name=pipe_name,
            status_id=lead.status_id,
            status_name=status_name,
            responsible_user_id=lead.responsible_user_id,
            responsible_user_name=user_name,
            contact_id=lead.contact_id,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            company_id=lead.company_id,
            company_name=None,
            unidade=lead.unidade,
            procedimento=lead.procedimento,
            origem=lead.origem,
            suborigem=lead.suborigem,
            loss_reason=lead.loss_reason,
            created_at=lead.created_at,
            closed_at=lead.closed_at,
            updated_at=lead.updated_at
        )

    async def list_leads(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        source_type: Optional[str] = None,
        consultora_id: Optional[int] = None,
        pipeline_id: Optional[int] = None,
        status_id: Optional[int] = None
    ) -> LeadListResponse:
        conditions = [Lead.organization_id == self.organization_id]

        if search:
            search_pattern = f"%{search}%"
            conditions.append(Lead.name.ilike(search_pattern))
        if source_type and source_type.lower() not in ("all", "todos", ""):
            conditions.append(Lead.source_type == source_type.lower())
        if consultora_id:
            conditions.append(Lead.responsible_user_id == consultora_id)
        if pipeline_id:
            conditions.append(Lead.pipeline_id == pipeline_id)
        if status_id:
            conditions.append(Lead.status_id == status_id)

        # Count total
        count_query = select(func.count(Lead.id)).where(and_(*conditions))
        total_res = await self.session.execute(count_query)
        total = total_res.scalar_one()

        # Query items
        offset = (page - 1) * page_size
        items_query = (
            select(Lead)
            .where(and_(*conditions))
            .order_by(desc(Lead.created_at))
            .offset(offset)
            .limit(page_size)
        )
        leads_res = await self.session.execute(items_query)
        leads = list(leads_res.scalars().all())

        # Build responses with lookup maps for efficiency
        pipe_res = await self.session.execute(
            select(Pipeline.id, Pipeline.name).where(Pipeline.organization_id == self.organization_id)
        )
        pipe_map = {p[0]: p[1] for p in pipe_res.all()}

        status_res = await self.session.execute(
            select(LeadStatus.id, LeadStatus.name).where(LeadStatus.organization_id == self.organization_id)
        )
        status_map = {s[0]: s[1] for s in status_res.all()}

        user_res = await self.session.execute(
            select(User.id, User.name).where(User.organization_id == self.organization_id)
        )
        user_map = {u[0]: u[1] for u in user_res.all()}

        items = []
        for l in leads:
            items.append(
                LeadResponse(
                    id=l.id,
                    organization_id=l.organization_id,
                    external_id=l.external_id,
                    source_type=l.source_type or "kommo",
                    name=l.name,
                    price=l.price,
                    pipeline_id=l.pipeline_id,
                    pipeline_name=pipe_map.get(l.pipeline_id),
                    status_id=l.status_id,
                    status_name=status_map.get(l.status_id),
                    responsible_user_id=l.responsible_user_id,
                    responsible_user_name=user_map.get(l.responsible_user_id),
                    contact_id=l.contact_id,
                    contact_name=None,
                    contact_phone=None,
                    contact_email=None,
                    company_id=l.company_id,
                    company_name=None,
                    unidade=l.unidade,
                    procedimento=l.procedimento,
                    origem=l.origem,
                    suborigem=l.suborigem,
                    loss_reason=l.loss_reason,
                    created_at=l.created_at,
                    closed_at=l.closed_at,
                    updated_at=l.updated_at
                )
            )

        return LeadListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )

    async def update_lead(self, lead_id: int, data: LeadUpdate) -> Optional[LeadResponse]:
        query = select(Lead).where(
            Lead.id == lead_id,
            Lead.organization_id == self.organization_id
        )
        res = await self.session.execute(query)
        lead = res.scalars().first()
        if not lead:
            return None

        prev_status_id = lead.status_id

        if data.name is not None:
            lead.name = data.name
        if data.price is not None:
            lead.price = data.price
        if data.pipeline_id is not None:
            lead.pipeline_id = data.pipeline_id
        if data.status_id is not None:
            lead.status_id = data.status_id
        if data.responsible_user_id is not None:
            lead.responsible_user_id = data.responsible_user_id
        if data.unidade is not None:
            lead.unidade = data.unidade
        if data.procedimento is not None:
            lead.procedimento = data.procedimento
        if data.origem is not None:
            lead.origem = data.origem
        if data.suborigem is not None:
            lead.suborigem = data.suborigem
        if data.loss_reason is not None:
            lead.loss_reason = data.loss_reason
        if data.closed_at is not None:
            lead.closed_at = data.closed_at
        if data.custom_fields_values is not None:
            lead.custom_fields_values = data.custom_fields_values

        lead.updated_at = datetime.now(timezone.utc)

        if data.status_id is not None and data.status_id != prev_status_id:
            status_res = await self.session.execute(
                select(LeadStatus).where(LeadStatus.id == data.status_id)
            )
            status_obj = status_res.scalars().first()
            if status_obj and (status_obj.type == 2 or "ganh" in status_obj.name.lower() or "vend" in status_obj.name.lower()):
                lead.closed_at = lead.closed_at or datetime.now(timezone.utc)

            history = LeadHistory(
                organization_id=self.organization_id,
                lead_id=lead.id,
                from_status_id=prev_status_id,
                to_status_id=data.status_id,
                changed_at=datetime.now(timezone.utc)
            )
            self.session.add(history)

        await self.session.commit()
        return await self.get_lead(lead.id)

    async def delete_lead(self, lead_id: int) -> bool:
        query = select(Lead).where(
            Lead.id == lead_id,
            Lead.organization_id == self.organization_id
        )
        res = await self.session.execute(query)
        lead = res.scalars().first()
        if not lead:
            return False

        await self.session.delete(lead)
        await self.session.commit()
        return True

    async def import_csv(self, file_content: bytes) -> CsvImportSummary:
        """Parses CSV text and creates leads under this organization."""
        text = None
        for enc in ("utf-8-sig", "utf-8", "latin-1", "iso-8859-1"):
            try:
                text = file_content.decode(enc)
                break
            except UnicodeDecodeError:
                continue

        if text is None:
            return CsvImportSummary(
                total_rows=0,
                imported_count=0,
                failed_count=0,
                errors=[CsvImportRowError(row_number=0, error="Codificação inválida do arquivo")]
            )

        # Detect separator (comma or semicolon)
        first_line = text.splitlines()[0] if text.splitlines() else ""
        delimiter = ";" if ";" in first_line and first_line.count(";") >= first_line.count(",") else ","

        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        
        # Load pipelines, statuses and users for name matching
        pipes_res = await self.session.execute(
            select(Pipeline).where(Pipeline.organization_id == self.organization_id)
        )
        pipes = {p.name.strip().lower(): p.id for p in pipes_res.scalars().all()}

        statuses_res = await self.session.execute(
            select(LeadStatus).where(LeadStatus.organization_id == self.organization_id)
        )
        statuses = {s.name.strip().lower(): (s.id, s.pipeline_id) for s in statuses_res.scalars().all()}

        users_res = await self.session.execute(
            select(User).where(User.organization_id == self.organization_id)
        )
        users = {u.name.strip().lower(): u.id for u in users_res.scalars().all()}

        default_pipe_id, default_status_id = await self._get_or_create_default_pipeline()

        total_rows = 0
        imported_count = 0
        failed_count = 0
        errors: List[CsvImportRowError] = []

        for idx, row in enumerate(reader, start=1):
            total_rows += 1
            # Normalize dictionary keys
            clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}

            # Find name
            name = (
                clean_row.get("nome")
                or clean_row.get("name")
                or clean_row.get("cliente")
                or clean_row.get("contato")
                or clean_row.get("lead")
            )
            if not name:
                errors.append(CsvImportRowError(row_number=idx, error="Nome do lead/cliente não informado", raw_data=row))
                failed_count += 1
                continue

            # Find price
            raw_price = (
                clean_row.get("valor")
                or clean_row.get("price")
                or clean_row.get("preco")
                or clean_row.get("receita")
                or "0"
            )
            try:
                clean_price_str = raw_price.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                price = float(clean_price_str) if clean_price_str else 0.0
            except ValueError:
                price = 0.0

            # Match status / pipeline
            raw_status = clean_row.get("status") or clean_row.get("etapa") or clean_row.get("fase") or ""
            raw_pipe = clean_row.get("pipeline") or clean_row.get("funil") or ""

            target_pipe_id = default_pipe_id
            if raw_pipe and raw_pipe.lower() in pipes:
                target_pipe_id = pipes[raw_pipe.lower()]

            target_status_id = default_status_id
            if raw_status and raw_status.lower() in statuses:
                s_id, p_id = statuses[raw_status.lower()]
                target_status_id = s_id
                target_pipe_id = p_id

            # Match consultora
            raw_user = clean_row.get("consultora") or clean_row.get("responsavel") or clean_row.get("vendedora") or ""
            target_user_id = users.get(raw_user.lower()) if raw_user else None

            # Unidade, Procedimento, Origem, Suborigem, Loss reason
            unidade = clean_row.get("unidade") or clean_row.get("unit")
            procedimento = clean_row.get("procedimento") or clean_row.get("servico") or clean_row.get("procedure")
            origem = clean_row.get("origem") or clean_row.get("source") or clean_row.get("canal") or "Planilha CSV"
            suborigem = clean_row.get("suborigem") or clean_row.get("suborigem")
            loss_reason = clean_row.get("motivo_perda") or clean_row.get("loss_reason") or clean_row.get("perda")

            is_won = False
            if raw_status and ("ganh" in raw_status.lower() or "vend" in raw_status.lower() or "fechad" in raw_status.lower()):
                is_won = True
            elif price > 0 and not loss_reason:
                is_won = True

            try:
                lead = Lead(
                    organization_id=self.organization_id,
                    name=name,
                    price=price,
                    pipeline_id=target_pipe_id,
                    status_id=target_status_id,
                    responsible_user_id=target_user_id,
                    source_type="csv",
                    unidade=unidade,
                    procedimento=procedimento,
                    origem=origem,
                    suborigem=suborigem,
                    loss_reason=loss_reason,
                    created_at=datetime.now(timezone.utc),
                    closed_at=datetime.now(timezone.utc) if is_won else None,
                    updated_at=datetime.now(timezone.utc)
                )
                self.session.add(lead)
                imported_count += 1
            except Exception as ex:
                errors.append(CsvImportRowError(row_number=idx, error=str(ex), raw_data=row))
                failed_count += 1

        await self.session.commit()

        return CsvImportSummary(
            total_rows=total_rows,
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors
        )
