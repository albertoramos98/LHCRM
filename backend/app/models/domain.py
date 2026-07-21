from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

# Association Table for Lead - Tag M:N
lead_tags = Table(
    "lead_tags",
    Base.metadata,
    Column("lead_id", Integer, ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="Consultora") # Admin, Gerente, Consultora
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="responsible_user")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="responsible_user")

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True)
    custom_fields_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="contacts")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="contact")

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    custom_fields_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="company")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="company")

class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)

    statuses: Mapped[List["LeadStatus"]] = relationship("LeadStatus", back_populates="pipeline", cascade="all, delete-orphan")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="pipeline")

class LeadStatus(Base):
    __tablename__ = "lead_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    pipeline_id: Mapped[int] = mapped_column(Integer, ForeignKey("pipelines.id"))
    name: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    type: Mapped[int] = mapped_column(Integer, default=1) # 1: active, 2: won, 3: lost

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="statuses")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="status")

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    
    pipeline_id: Mapped[int] = mapped_column(Integer, ForeignKey("pipelines.id"))
    status_id: Mapped[int] = mapped_column(Integer, ForeignKey("lead_status.id"))
    responsible_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    contact_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("contacts.id"), nullable=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True)

    # Key attributes for executive breakdown
    unidade: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    procedimento: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    origem: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    suborigem: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    loss_reason: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)

    first_response_time_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sales_cycle_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    custom_fields_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="leads")
    status: Mapped["LeadStatus"] = relationship("LeadStatus", back_populates="leads")
    responsible_user: Mapped[Optional["User"]] = relationship("User", back_populates="leads")
    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="leads")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="leads")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=lead_tags, back_populates="leads")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="lead")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="lead")
    history: Mapped[List["LeadHistory"]] = relationship("LeadHistory", back_populates="lead")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    lead_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("leads.id"), nullable=True)
    responsible_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolution_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="tasks")
    responsible_user: Mapped[Optional["User"]] = relationship("User", back_populates="tasks")

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    lead_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("leads.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(100), index=True) # e.g. lead_status_changed, note_added
    value_before: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_after: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="events")

class CustomField(Base):
    __tablename__ = "custom_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    field_type: Mapped[str] = mapped_column(String(50)) # text, numeric, select, etc.

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    leads: Mapped[List["Lead"]] = relationship("Lead", secondary=lead_tags, back_populates="tags")

class LeadHistory(Base):
    __tablename__ = "lead_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id"))
    from_status_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("lead_status.id"), nullable=True)
    to_status_id: Mapped[int] = mapped_column(Integer, ForeignKey("lead_status.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="history")

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(50), default="automatic") # manual, automatic
    status: Mapped[str] = mapped_column(String(50), default="in_progress") # in_progress, success, failed
    items_synced: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
