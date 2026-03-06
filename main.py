from fastapi import FastAPI


app = FastAPI(title="Events Aggregator")


# Старт проекта
@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
