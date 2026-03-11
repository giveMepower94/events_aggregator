from fastapi import APIRouter, BackgroundTasks

from src.events_agg.usecases.run_sync_job import run_sync_job

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/trigger", status_code=202)
async def trigger_sync(background_tasks: BackgroundTasks) -> dict[str, str]:
    background_tasks.add_task(run_sync_job)
    return {"status": "accepted"}
