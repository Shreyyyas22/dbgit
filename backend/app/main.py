from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from .config import settings
from .api.v1 import api_router

# Setup structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup events
    await logger.ainfo("Starting up dbgit API...", environment=settings.environment)
    # Initialize DB connection, Kafka, Redis here later
    yield
    # Shutdown events
    await logger.ainfo("Shutting down dbgit API...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="dbgit API",
        description="Git for Databases — version control for your data",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()
