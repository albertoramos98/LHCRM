import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class CRMIntegration(Base):
    __tablename__ = "crm_integrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(36), index=True, default=lambda: str(uuid.uuid4()))
    provider: Mapped[str] = mapped_column(String(50), default="kommo", index=True)
    subdomain: Mapped[str] = mapped_column(String(255), index=True)
    client_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    client_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    redirect_uri: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="disconnected", index=True) # connected, disconnected, expired, error
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    logs: Mapped[List["IntegrationLog"]] = relationship("IntegrationLog", back_populates="integration", cascade="all, delete-orphan")

class IntegrationLog(Base):
    __tablename__ = "integration_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    integration_id: Mapped[str] = mapped_column(String(36), ForeignKey("crm_integrations.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(100), index=True) # connection_established, oauth_error, api_error, token_refreshed, sync_started, sync_completed
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="info") # info, success, warning, error
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    integration: Mapped["CRMIntegration"] = relationship("CRMIntegration", back_populates="logs")
