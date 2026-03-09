from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.db.session import get_session
from src.events_agg.repositories.events import EventsRepository
from src.events_agg.schemas.events import (
    EventListItemSchema,
    EventDeatailSchema,
    PlaceShortSchema,
    PlaceSchema,
    PaginatedEventsSchema)


router = APIRouter(prefix="/api/events", tags=["events"])


def build_event_item(event) -> EventListItemSchema:
    return EventListItemSchema(
        id=event.id,
        name=event.name,
        place=PlaceShortSchema(
            id=event.place.id,
            name=event.place.name,
            city=event.place.city,
            address=event.place.address,
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )


@router.get("/", response_model=PaginatedEventsSchema)
async def list_events(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    date_from: date | None = Query(default=None),
    session: AsyncSession = Depends(get_session)
) -> PaginatedEventsSchema:

    repo = EventsRepository(session)
    items, total = await repo.list_paginated(
        page=page,
        page_size=page_size,
        date_from=date_from
    )

    next_url = f"/api/events?page={page + 1}&page_size={page_size}" if page * page_size < total else None
    previous_url = (
        f"/api/events?page={page - 1}&page_size={page_size}"
        if page > 1
        else None
    )

    if date_from:
        suffix = f"&date_from={date_from.isoformat()}"
        if next_url:
            next_url += suffix
        if previous_url:
            previous_url += suffix

    return PaginatedEventsSchema(
        count=total,
        next=next_url,
        previous=previous_url,
        results=[build_event_item(event) for event in items]
    )


@router.get("/{event_id}", response_model=EventDeatailSchema)
async def get_event(
    event_id: str,
    session: AsyncSession = Depends(get_session)
) -> EventDeatailSchema:

    repo = EventsRepository(session)
    event = await repo.get(event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventDeatailSchema(
        id=event.id,
        name=event.name,
        place=PlaceSchema(
            id=event.place.id,
            name=event.place.name,
            city=event.place.city,
            address=event.place.address,
            seats_pattern=event.place.seats_pattern,
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )
