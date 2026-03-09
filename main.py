from contextlib import asynccontextmanager
from fastapi import FastAPI

from pydantic import BaseModel
from src.events_agg.db.session import engine
from src.events_agg.db.base import Base
from src.events_agg.api.routes.events import router as events_router
from src.events_agg.api.routes.sync import router as sync_router

from src.events_agg.models.event import Event, Place  # noqa: F401
from src.events_agg.models.sync_state import SyncState  # noqa: F401


class HealthResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Events Aggregator", lifespan=lifespan)

app.include_router(events_router)
app.include_router(sync_router)


# Старт проекта
@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
