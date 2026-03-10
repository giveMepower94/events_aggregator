from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.core.seats import seat_exists_in_pattern
from src.events_agg.core.state import seats_cache
from src.events_agg.repositories.events import EventsRepository
from src.events_agg.repositories.tickets import TicketsRepository

from src.events_agg.schemas.tickets import CreateTicketRequestSchema, CreateTicketResponseSchema


class CreateTicketUseCase:
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

    async def execute(
        self,
        data: CreateTicketRequestSchema,
    ) -> CreateTicketResponseSchema:
        event = await self.events.get(data.event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status != "published":
            raise HTTPException(
                status_code=400,
                detail="Registration is available only for published events",
            )

        now = datetime.now(timezone.utc)
        event_time = event.event_time
        registration_deadline = event.registration_deadline

        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)

        if registration_deadline.tzinfo is None:
            registration_deadline = registration_deadline.replace(tzinfo=timezone.utc)

        if now >= registration_deadline:
            raise HTTPException(status_code=400, detail="Registration deadline has passed")

        if now >= event_time:
            raise HTTPException(status_code=400, detail="Event has already started")

        if not seat_exists_in_pattern(data.seat, event.place.seats_pattern):
            raise HTTPException(status_code=400, detail="Seat does not exist")

        seats_response = await self.client.get_seats(data.event_id)
        if data.seat not in seats_response.seats:
            raise HTTPException(status_code=400, detail="Seat is not available")

        provider_response = await self.client.register(
            event_id=data.event_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            seat=data.seat,
        )

        await self.tickets.create(
            ticket_id=provider_response.ticket_id,
            event_id=data.event_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            seat=data.seat,
        )
        await self.session.commit()

        seats_cache.delete(f"event_seats:{data.event_id}")

        return CreateTicketResponseSchema(ticket_id=provider_response.ticket_id)