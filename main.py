from fastapi import FastAPI

from pydantic import BaseModel

from src.events_agg.api.routes.events import router as events_router
from src.events_agg.api.routes.sync import router as sync_router


class HealthResponse(BaseModel):
    status: str


app = FastAPI(title="Events Aggregator")

app.include_router(events_router)
app.include_router(sync_router)


# Старт проекта
@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
