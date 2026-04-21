"""
AI Automation Backend Platform
Main FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import messages, webhooks, health, analytics
from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    setup_logging()
    await init_db()
    await init_redis()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Automation Backend Platform",
        description="Hybrid AI system for automated customer engagement",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    app.include_router(health.router,     prefix="/api/v1", tags=["Health"])
    app.include_router(messages.router,   prefix="/api/v1", tags=["Messages"])
    app.include_router(webhooks.router,   prefix="/api/v1", tags=["Webhooks"])
    app.include_router(analytics.router,  prefix="/api/v1", tags=["Analytics"])

    return app


app = create_app()
