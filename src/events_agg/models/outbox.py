from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.events_agg.db.base import Base


class OutboxMessage(Base):
    __tablename__ = "outbox"
    __table_args__ = (
        Index("ix_outbox_status_created_at", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    event_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_error: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )
