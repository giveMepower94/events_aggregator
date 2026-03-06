from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.events_agg.db.session import get_session

from fastapi import FastAPI


app = FastAPI(title="Events Aggregator")


# Старт проекта
@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/db-check")
async def db_check(session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(text("SELECT 1"))
    return {"db": result.scalar_one()}
