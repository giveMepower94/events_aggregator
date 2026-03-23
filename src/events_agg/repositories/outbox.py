from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.models.outbox import OutboxMessage
from src.events_agg.models.ticket import Ticket


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_ticket_purchased(
        self,
        ticket: Ticket,
        event_name: str
    ) -> OutboxMessage:
        message = OutboxMessage(
            event_type="ticket_purchased",
            payload={
                "ticket_id": ticket.ticket_id,
                "event_id": ticket.event_id,
                "email": ticket.email,
                "first_name": ticket.first_name,
                "last_name": ticket.last_name,
                "seat": ticket.seat,
                "event_name": event_name,
                "message": f"Вы успешно зарегистрированы на мероприятие - {event_name}"
            },
            status="pending",
            attempts=0,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def list_pending(self, limit: int) -> list[OutboxMessage]:
        stmt = (
            select(OutboxMessage)
            .where(OutboxMessage.status == "pending")
            .order_by(OutboxMessage.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_sent(self, message: OutboxMessage) -> None:
        message.status = "sent"
        message.sent_at = datetime.now(timezone.utc)
        message.last_error = None
        await self.session.flush()

    async def mark_failed(self, message: OutboxMessage, error_text: str) -> None:
        message.attempts += 1
        message.last_error = error_text[:1000]
        await self.session.flush()
