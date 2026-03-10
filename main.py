from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from src.events_agg.api.routes.events import router as events_router
from src.events_agg.api.routes.sync import router as sync_router
from src.events_agg.api.routes.tickets import router as tickets_router
from src.events_agg.core.scheduler import create_scheduler


class HealthResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(title="Events Aggregator", lifespan=lifespan)

app.include_router(events_router)
app.include_router(sync_router)
app.include_router(tickets_router)


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")

