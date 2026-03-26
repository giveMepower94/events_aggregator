from src.events_agg.clients.events_provider import EventsProviderClient


def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient()
