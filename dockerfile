FROM python:3.11-slim

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

RUN pip install --no-cache-dir uv && \
    uv sync --frozen

USER appuser

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]