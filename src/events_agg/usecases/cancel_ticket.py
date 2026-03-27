from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.core.exceptions import (
    CancellationNotAllowedError,
    EventNotFoundError,
    TicketNotFoundError,
)
from src.events_agg.core.state import seats_cache
from src.events_agg.repositories.events import EventsRepository
from src.events_agg.repositories.tickets import TicketsRepository
from src.events_agg.schemas.tickets import CancelTicketResponseSchema


class CancelTicketUseCase:
    def __init__(
        self,
        session: AsyncSession,
        events: EventsRepository,
        tickets: TicketsRepository,
        client: EventsProviderClient,
    ) -> None:
        self.session = session
        self.events = events
        self.tickets = tickets
        self.client = client

    async def execute(self, ticket_id: str) -> CancelTicketResponseSchema:
        ticket = await self.tickets.get_by_ticket_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError()

        event = await self.events.get(ticket.event_id)
        if event is None:
            raise EventNotFoundError()

        event_time = event.event_time
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        if now >= event_time:
            raise CancellationNotAllowedError()

        await self.client.unregister(event_id=event.id, ticket_id=ticket_id)
        await self.tickets.delete(ticket)
        await self.session.commit()

        seats_cache.delete(f"event_seats:{event.id}")

        return CancelTicketResponseSchema(success=True)

