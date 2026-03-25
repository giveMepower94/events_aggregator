import asyncio
import logging
from contextlib import asynccontextmanager

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

from src.events_agg.api.routes.events import router as events_router
from src.events_agg.api.routes.sync import router as sync_router
from src.events_agg.api.routes.tickets import router as tickets_router
from src.events_agg.core.config import settings
from src.events_agg.core.scheduler import create_scheduler
from src.events_agg.usecases.run_outbox_worker import run_outbox_worker

logger = logging.getLogger(__name__)

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        environment=settings.app_env,
        traces_sample_rate=0.0,
    )


class HealthResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()

    stop_event = asyncio.Event()
    outbox_worker_task = asyncio.create_task(run_outbox_worker(stop_event))

    try:
        yield
    finally:
        stop_event.set()

        try:
            await outbox_worker_task
        except Exception:
            logger.exception("Outbox worker stopped with error")

        scheduler.shutdown()


app = FastAPI(title="Events Aggregator", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )

app.include_router(events_router)
app.include_router(sync_router)
app.include_router(tickets_router)


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
