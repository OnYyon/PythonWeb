from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.payment.api.routers.cards import router as cards_router
from src.payment.api.routers.payments import router as payments_router
from src.payment.config import Settings
from src.payment.infrastructure.db import Database
from src.shared.utils.logger import LoggerConfig, configure_logger, get_logger


def create_app() -> FastAPI:
    configure_logger(LoggerConfig(service_name="payment"))
    logger = get_logger("payment")

    settings = Settings.from_env()
    db = Database(
        dsn=settings.database_dsn,
        min_size=settings.pool_min_size,
        max_size=settings.pool_max_size,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("payment_startup")
        await db.connect()
        app.state.db = db
        yield
        await db.disconnect()
        logger.info("payment_shutdown")

    api_prefix = "/api/v1"

    app = FastAPI(
        title="Payment Service",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=f"{api_prefix}/docs",
        openapi_url=f"{api_prefix}/openapi.json",
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid4())
        bind_contextvars(request_id=request_id)
        try:
            response: Response = await call_next(request)
        finally:
            clear_contextvars()
        response.headers["X-Request-Id"] = request_id
        return response

    app.include_router(cards_router, prefix=api_prefix)
    app.include_router(payments_router, prefix=api_prefix)

    return app


app = create_app()
