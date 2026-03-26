from datetime import datetime, timezone

import pytest

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.schemas.provider import (
    ProviderEventSchema,
    ProviderEventsPageSchema,
    ProviderPlaceSchema
)


def build_place() -> ProviderPlaceSchema:
    now = datetime.now(timezone.utc)
    return ProviderPlaceSchema(
        id="place-1",
        name="Test Place",
        city="Moscow",
        address="Test address",
        seats_pattern="A1,A2,A3",
        changed_at=now,
        created_at=now,
    )


def build_event(event_id: str) -> ProviderEventSchema:
    now = datetime.now(timezone.utc)
    return ProviderEventSchema(
        id=event_id,
        name=f"Event {event_id}",
        place=build_place(),
        event_time=now,
        registration_deadline=now,
        status="published",
        number_of_visitors=0,
        changed_at=now,
        created_at=now,
        status_changed_at=now,
    )


@pytest.mark.asyncio
async def test_iter_events_yields_events_from_all_pages(monkeypatch):
    client = EventsProviderClient()

    pages = {
        None: ProviderEventsPageSchema(
            next="page-2",
            previous=None,
            results=[build_event("event-1"), build_event("event-2")]
        ),
        "page-2": ProviderEventsPageSchema(
            next=None,
            previous="page-1",
            results=[build_event("event-3")]
        ),
    }

    async def fake_get_events_page(changed_at: str, url: str | None = None):
        return pages[url]

    monkeypatch.setattr(client, "get_events_page", fake_get_events_page)

    result = [event async for event in client.iter_events(changed_at="1970-01-01")]

    assert [event.id for event in result] == ["event-1", "event-2", "event-3"]


@pytest.mark.asyncio
async def test_iter_events_stops_when_next_is_none(monkeypatch):
    client = EventsProviderClient()

    async def fake_get_events_page(changed_at: str, url: str | None = None):
        return ProviderEventsPageSchema(
            next=None,
            previous=None,
            results=[build_event("event-1")]
        )

    monkeypatch.setattr(client, "get_events_page", fake_get_events_page)

    result = [event async for event in client.iter_events(changed_at="1970-01-01")]

    assert len(result) == 1
    assert result[0].id == "event-1"


@pytest.mark.asyncio
async def test_iter_events_returns_empty_when_provider_returns_empty_page(monkeypatch):
    client = EventsProviderClient()

    async def fake_get_events_page(changed_at: str, url: str | None = None):
        return ProviderEventsPageSchema(
            next=None,
            previous=None,
            results=[]
        )

    monkeypatch.setattr(client, "get_events_page", fake_get_events_page)

    result = [event async for event in client.iter_events(changed_at="1970-01-01")]

    assert len(result) == 0
