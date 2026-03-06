from fastapi import FastAPI

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


app = FastAPI(title="Events Aggregator", responses_model={200: HealthResponse})


# Старт проекта
@app.get("/api/health")
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
