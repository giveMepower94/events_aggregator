from collections.abc import AsyncIterator
from src.events_agg.schemas.provider import ProviderEventSchema


class EventsPaginator:
    def __init__(
        self,
        client,
        changed_at: str
    ) -> None:
        self.client = client
        self.changed_at = changed_at
        self.next_url: str | None = None
        self._buffer: list[ProviderEventSchema] = []
        self._finished = False
        self._started = False

    def __aiter__(self) -> AsyncIterator[ProviderEventSchema]:
        return self

    async def __anext__(self) -> ProviderEventSchema:
        while not self._buffer and not self._finished:
            page = await self.client.get_events_page(
                changed_at=self.changed_at,
                url=self.next_url,
            )
            self._started = True
            self._buffer.extend(page.results)

            if page.next is None:
                self._finished = True
            else:
                self.next_url = page.next

        if self._buffer:
            return self._buffer.pop(0)

        raise StopAsyncIteration
