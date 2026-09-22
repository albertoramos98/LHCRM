from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Table, Column, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# Association Table for Lead - Tag M:N
lead_tags = Table(
    "lead_tags",
    Base.metadata,
    Column("lead_id", Integer, ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    members: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    users: Mapped[List["User"]] = relationship("User", back_populates="organization", foreign_keys="User.organization_id")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="organization", cascade="all, delete-orphan")
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="organization", cascade="all, delete-orphan")
    companies: Mapped[List["Company"]] = relationship("Company", back_populates="organization", cascade="all, delete-orphan")
    pipelines: Mapped[List["Pipeline"]] = relationship("Pipeline", back_populates="organization", cascade="all, delete-orphan")
    lead_statuses: Mapped[List["LeadStatus"]] = relationship("LeadStatus", back_populates="organization", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="organization", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="organization", cascade="all, delete-orphan")
    custom_fields: Mapped[List["CustomField"]] = relationship("CustomField", back_populates="organization", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship("Tag", back_populates="organization", cascade="all, delete-orphan")
    sync_logs: Mapped[List["SyncLog"]] = relationship("SyncLog", back_populates="organization", cascade="all, delete-orphan")
    macro_metrics: Mapped[List["MacroMetric"]] = relationship("MacroMetric", back_populates="organization", cascade="all, delete-orphan")

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(50), default="Consultora") # Owner, Admin, Gerente, Consultora
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member_org_user"),
    )

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="Consultora") # Owner, Admin, Gerente, Consultora
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users", foreign_keys=[organization_id])
    memberships: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="user", cascade="all, delete-orphan")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="responsible_user")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="responsible_user")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_user_org_external_id"),
    )

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    custom_fields_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="contacts")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="contacts")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="contact")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_contact_org_ext_id"),
        Index("ix_contacts_org_created", "organization_id", "created_at"),
    )

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    custom_fields_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="companies")
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="company")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="company")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_company_org_ext_id"),
    )

class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="pipelines")
    statuses: Mapped[List["LeadStatus"]] = relationship("LeadStatus", back_populates="pipeline", cascade="all, delete-orphan")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="pipeline")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_pipeline_org_ext_id"),
    )

class LeadStatus(Base):
    __tablename__ = "lead_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    pipeline_id: Mapped[int] = mapped_column(Integer, ForeignKey("pipelines.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    type: Mapped[int] = mapped_column(Integer, default=1) # 1: active, 2: won, 3: lost

    organization: Mapped["Organization"] = relationship("Organization", back_populates="lead_statuses")
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="statuses")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="status")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_lead_status_org_ext_id"),
    )

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    
    pipeline_id: Mapped[int] = mapped_column(Integer, ForeignKey("pipelines.id", ondelete="CASCADE"))
    status_id: Mapped[int] = mapped_column(Integer, ForeignKey("lead_status.id", ondelete="CASCADE"))
    responsible_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)

    # Key attributes for executive breakdown
    source_type: Mapped[str] = mapped_column(String(50), default="kommo", index=True) # kommo, manual, csv
    unidade: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    procedimento: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    origem: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    suborigem: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    loss_reason: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)

    first_response_time_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sales_cycle_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    custom_fields_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="leads")
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="leads")
    status: Mapped["LeadStatus"] = relationship("LeadStatus", back_populates="leads")
    responsible_user: Mapped[Optional["User"]] = relationship("User", back_populates="leads")
    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="leads")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="leads")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=lead_tags, back_populates="leads")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="lead", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="lead", cascade="all, delete-orphan")
    history: Mapped[List["LeadHistory"]] = relationship("LeadHistory", back_populates="lead", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_lead_org_ext_id"),
        Index("ix_leads_org_created", "organization_id", "created_at"),
        Index("ix_leads_org_status", "organization_id", "status_id"),
        Index("ix_leads_org_resp_user", "organization_id", "responsible_user_id"),
        Index("ix_leads_org_pipeline", "organization_id", "pipeline_id"),
    )

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    lead_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)
    responsible_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="tasks")
    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="tasks")
    responsible_user: Mapped[Optional["User"]] = relationship("User", back_populates="tasks")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_task_org_ext_id"),
        Index("ix_tasks_org_completed_due", "organization_id", "is_completed", "due_date"),
    )

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    lead_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(100), index=True) # e.g. lead_status_changed, note_added
    value_before: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_after: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="events")
    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="events")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_event_org_ext_id"),
    )

class CustomField(Base):
    __tablename__ = "custom_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    field_type: Mapped[str] = mapped_column(String(50)) # text, numeric, select, etc.

    organization: Mapped["Organization"] = relationship("Organization", back_populates="custom_fields")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_custom_field_org_ext_id"),
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="tags")
    leads: Mapped[List["Lead"]] = relationship("Lead", secondary=lead_tags, back_populates="tags")

    __table_args__ = (
        UniqueConstraint("organization_id", "external_id", name="uq_tag_org_ext_id"),
    )

class LeadHistory(Base):
    __tablename__ = "lead_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    from_status_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("lead_status.id", ondelete="SET NULL"), nullable=True)
    to_status_id: Mapped[int] = mapped_column(Integer, ForeignKey("lead_status.id", ondelete="CASCADE"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="history")

    __table_args__ = (
        Index("ix_lead_history_org_lead", "organization_id", "lead_id"),
    )

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(50), default="automatic") # manual, automatic
    status: Mapped[str] = mapped_column(String(50), default="in_progress") # in_progress, success, failed
    items_synced: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="sync_logs")

    __table_args__ = (
        Index("ix_sync_logs_org_started", "organization_id", "started_at"),
    )

class MacroMetric(Base):
    __tablename__ = "macro_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    period_month: Mapped[str] = mapped_column(String(7), index=True) # YYYY-MM
    consultora_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    revenue_target: Mapped[float] = mapped_column(Float, default=0.0)
    leads_target: Mapped[int] = mapped_column(Integer, default=0)
    sales_target: Mapped[int] = mapped_column(Integer, default=0)
    marketing_investment: Mapped[float] = mapped_column(Float, default=0.0)
    fixed_costs: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="macro_metrics")
    consultora: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        UniqueConstraint("organization_id", "period_month", "consultora_id", name="uq_macro_metric_org_month_user"),
        Index("ix_macro_metrics_org_month", "organization_id", "period_month"),
    )

