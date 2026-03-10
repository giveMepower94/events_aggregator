from collections.abc import AsyncIterator

import httpx

from src.events_agg.schemas.provider import (
    ProviderEventsPageSchema,
    ProviderRegisterResponseSchema,
    ProviderSeatsSchema,
    ProviderUnregisterResponseSchema
)


from src.events_agg.core.config import settings


class EventsProviderClient:
    def __init__(self) -> None:
        self.base_url = settings.events_provider_base_url.rstrip('/')
        self.api_key = settings.events_provider_api_key

    @property
    def headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_events_page(self, changed_at: str, url: str | None = None) -> ProviderEventsPageSchema:
        request_url = url or f"{self.base_url}/api/events/"

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            if url is None:
                response = await client.get(
                    request_url,
                    headers=self.headers,
                    params={"changed_at": changed_at},
                )
            else:
                response = await client.get(
                    request_url,
                    headers=self.headers,
                )

        response.raise_for_status()
        return ProviderEventsPageSchema.model_validate(response.json())

    async def iter_events(self, changed_at: str) -> AsyncIterator:
        next_url: str | None = None

        while True:
            page = await self.get_events_page(changed_at=changed_at, url=next_url)
            for event in page.results:
                yield event

            if page.next is None:
                break

            next_url = page.next

    async def get_seats(self, event_id: str) -> ProviderSeatsSchema:
        url = f"{self.base_url}/api/events/{event_id}/seats/"

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(url, headers=self.headers)

        response.raise_for_status()
        return ProviderSeatsSchema.model_validate(response.json())

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> ProviderRegisterResponseSchema:
        url = f"{self.base_url}/api/events/{event_id}/register/"
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
            response = await client.post(url, headers=self.headers, json=payload)

        response.raise_for_status()
        return ProviderRegisterResponseSchema.model_validate(response.json())

    async def unregister(
        self,
        event_id: str,
        ticket_id: str,
    ) -> ProviderUnregisterResponseSchema:
        url = f"{self.base_url}/api/events/{event_id}/unregister/"
        payload = {"ticket_id": ticket_id}

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.request(
                "DELETE",
                url,
                headers=self.headers,
                json=payload,
            )

        response.raise_for_status()
        return ProviderUnregisterResponseSchema.model_validate(response.json())
