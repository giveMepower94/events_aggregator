from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.events_agg.clients.events_provider import EventsProviderClient
from src.events_agg.repositories.events import EventsRepository
from src.events_agg.repositories.sync_state import SyncStateRepository


class SyncEventsUseCase:
    def __init__(
        self,
        session: AsyncSession,
        client: EventsProviderClient,
    ) -> None:
        self.session = session
        self.client = client
        self.events = EventsRepository(session)
        self.sync_state = SyncStateRepository(session)

    async def execute(self) -> dict[str, int | str]:
        state = await self.sync_state.get_or_create()

        changed_at = (
            state.last_changed_at.date().isoformat()
            if state.last_changed_at is not None
            else "1970-01-01"
        )

        await self.sync_state.update_status(sync_status="running")
        await self.session.commit()

        processed = 0
        max_changed_at = state.last_changed_at

        try:
            async for provider_event in self.client.iter_events(changed_at=changed_at):
                await self.events.upsert_event(provider_event)
                processed += 1

                if max_changed_at is None or provider_event.changed_at > max_changed_at:
                    max_changed_at = provider_event.changed_at

            await self.sync_state.update_status(
                sync_status="success",
                last_sync_time=datetime.now(timezone.utc),
                last_changed_at=max_changed_at,
            )
            await self.session.commit()

        except Exception:
            await self.sync_state.update_status(
                sync_status="failed",
                last_sync_time=datetime.now(timezone.utc),
            )
            await self.session.commit()
            raise

        return {
            "status": "success",
            "processed": processed,
        }
