from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

# ========== 1️⃣ 请求体模型（FastAPI 422 用） ==========
class LyEvent(BaseModel):
    id: str
    rule_desc: str
    threat_source: str
    victim_target: str
    event_type: str
    detail_type: str
    method: str
    event_level: str
    occurrence_time: str

    model_config = {
        "extra": "ignore"
    }

# ========== 2️⃣ 去重映射表 ==========
class EventMap(Base):
    __tablename__ = "event_map"

    fingerprint: Mapped[str] = mapped_column(
        String(64),
        primary_key=True
    )

    ly_event_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )

    deepsoc_event_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

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

