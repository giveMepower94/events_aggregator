from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.events_agg.db.base import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        Index("ix_idempotency_status_created_at", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    request_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="processing",
        index=True
    )
    ticket_id: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
