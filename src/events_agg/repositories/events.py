from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.events_agg.models.event import Event, Place
from src.events_agg.schemas.provider import ProviderEventSchema


class EventsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, event_id: int) -> Event | None:
        stmt = (
            select(Event)
            .options(selectinload(Event.place))
            .where(Event.id == event_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        date_from: datetime | None = None
    ) -> tuple[list[Event], int]:

        stmt = (select(Event).options(selectinload(Event.place)))

        count_stmt = select(func.count()).select_from(Event)

        if date_from is not None:
            stmt = stmt.where(func.date(Event.event_time) >= date_from)
            count_stmt = count_stmt.where(
                func.date(Event.event_time) >= date_from
            )

        stmt = (
            stmt.order_by(Event.event_time.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        items_result = await self.session.execute(stmt)
        count_result = await self.session.execute(count_stmt)

        items = list(items_result.scalars().all())
        total = count_result.scalar_one()

        return items, total

    async def upsert_event(self, provider_event: ProviderEventSchema) -> None:
        place = await self.session.get(Place, provider_event.place.id)

        if place is None:
            place = Place(
                id=provider_event.place.id,
                name=provider_event.place.name,
                city=provider_event.place.city,
                address=provider_event.place.address,
                seats_pattern=provider_event.place.seats_pattern,
                changed_at=provider_event.place.changed_at,
                created_at=provider_event.place.created_at,
            )
            self.session.add(place)
        else:
            place.name = provider_event.place.name
            place.city = provider_event.place.city
            place.address = provider_event.place.address
            place.seats_pattern = provider_event.place.seats_pattern
            place.changed_at = provider_event.place.changed_at
            place.created_at = provider_event.place.created_at

        event = await self.session.get(Event, provider_event.id)

        if event is None:
            event = Event(
                id=provider_event.id,
                name=provider_event.name,
                event_time=provider_event.event_time,
                registration_deadline=provider_event.registration_deadline,
                status=provider_event.status,
                number_of_visitors=provider_event.number_of_visitors,
                changed_at=provider_event.changed_at,
                created_at=provider_event.created_at,
                status_changed_at=provider_event.status_changed_at,
                place_id=provider_event.place.id,
            )
            self.session.add(event)
        else:
            event.name = provider_event.name
            event.event_time = provider_event.event_time
            event.registration_deadline = provider_event.registration_deadline
            event.status = provider_event.status
            event.number_of_visitors = provider_event.number_of_visitors
            event.changed_at = provider_event.changed_at
            event.created_at = provider_event.created_at
            event.status_changed_at = provider_event.status_changed_at
            event.place_id = provider_event.place.id

