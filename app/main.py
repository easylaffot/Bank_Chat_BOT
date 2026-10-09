"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.products import router as products_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Log application startup and shutdown through FastAPI's lifespan hooks."""
    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)
    yield
    logger.info("Shutting down %s", settings.app_name)


async def app_metadata() -> dict[str, str]:
    return {"app": settings.app_name, "status": "running"}


async def health_status() -> dict[str, str]:
    return {"status": "healthy"}


api_v1_router = APIRouter()
api_v1_router.add_api_route("/", app_metadata, methods=["GET"], include_in_schema=False)
api_v1_router.add_api_route(
    "/health",
    health_status,
    methods=["GET"],
    tags=["Health"],
)
api_v1_router.include_router(products_router)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend foundation for the Agentic AI E-Commerce Shopping Assistant.",
    lifespan=lifespan,
)
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["Service"])
async def root() -> dict[str, str]:
    return await app_metadata()


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return await health_status()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception for %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
