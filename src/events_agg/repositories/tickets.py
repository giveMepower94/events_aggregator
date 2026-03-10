from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.models.ticket import Ticket


class TicketsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_tickets_by_event_id(self, ticked_id: int) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.ticket_id == ticked_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_ticket(self, event_id: int, price: float) -> Ticket:
        new_ticket = Ticket(event_id=event_id, price=price, created_at=datetime.now(timezone.utc))
        self.session.add(new_ticket)
        await self.session.commit()
        await self.session.refresh(new_ticket)
        return new_ticket

    async def create(
        self,
        ticket_id: str,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> Ticket:
        ticket = Ticket(
            ticket_id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(ticket)
        await self.session.flush()
        return ticket

    async def delete(self, ticket: Ticket) -> None:
        await self.session.delete(ticket)
        await self.session.flush()
