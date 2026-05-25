from __future__ import annotations

import logging
import os
import time

from fastapi import FastAPI, Request

from src.auth_service.auth_router import router as auth_router
from src.auth_service.role_router import router as role_router

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auth Service", version="1.0.0", description="Token issue/validation service")


@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "http.request method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


app.include_router(auth_router)
app.include_router(role_router)


@app.get("/health", tags=["service"])
def health() -> dict[str, str]:
    return {"status": "ok"}

