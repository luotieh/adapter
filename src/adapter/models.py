from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class SyncCursor(Base):
    __tablename__ = "sync_cursor"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, default="flowshadow_events")
    last_ts: Mapped[str] = mapped_column(String(64), default="")  # ISO8601 or other cursor string
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PushedEvent(Base):
    __tablename__ = "pushed_events"
    ly_event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), index=True)
    deepsoc_event_id: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[str] = mapped_column(String(16), default="SUCCESS")  # SUCCESS/FAILED
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_idempotency_key"),)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(128), default="unknown")  # user/service
    action: Mapped[str] = mapped_column(String(64))  # QUERY_FLOW / GET_PCAP / QUERY_ASSET / etc.
    target: Mapped[str] = mapped_column(String(256))  # flow_id / ip / pcap_id
    meta: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
