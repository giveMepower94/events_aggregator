from fastapi import HTTPException

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.core.config import settings
from src.events_agg.core.state import seats_cache
from src.events_agg.repositories.events import EventsRepository
from src.events_agg.schemas.seats import EventSeatsResponseSchema


class GetEventSeatsUseCase:
    def __init__(
        self,
        events: EventsRepository,
        client: EventsProviderClient,
    ) -> None:
        self.events = events
        self.client = client

    async def execute(self, event_id: str) -> EventSeatsResponseSchema:
        event = await self.events.get(event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status != "published":
            raise HTTPException(
                status_code=400,
                detail="Seats are available only for published events",
            )

        cache_key = f"event_seats:{event_id}"
        cached = seats_cache.get(cache_key)
        if cached is not None:
            return EventSeatsResponseSchema(
                event_id=event_id,
                available_seats=cached,
            )

        provider_response = await self.client.get_seats(event_id)
        seats_cache.set(
            cache_key,
            provider_response.seats,
            ttl_seconds=settings.seats_cache_ttl_seconds,
        )

        return EventSeatsResponseSchema(
            event_id=event_id,
            available_seats=provider_response.seats,
        )
