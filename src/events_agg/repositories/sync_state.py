from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.events_agg.models.sync_state import SyncState


class SyncStateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self) -> SyncState:
        stmt = select(SyncState).where(SyncState.id == 1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self) -> SyncState:
        state = await self.get()
        if state is None:
            state = SyncState(
                id=1,
                last_sync_time=None,
                last_changed_at=None,
                sync_status="never",
            )
            self.session.add(state)
            await self.session.flush()

        return state

    async def update_status(
        self,
        sync_status: str,
        last_sync_time: datetime | None = None,
        last_changed_at: datetime | None = None,
    ) -> SyncState:
        state = await self.get_or_create()
        state.sync_status = sync_status

        if last_sync_time is not None:
            state.last_sync_time = last_sync_time

        if last_changed_at is not None:
            state.last_changed_at = last_changed_at

        await self.session.flush()
        return state

