from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    alert_channels,
    api_keys,
    auth,
    daily_stats,
    hourly_stats,
    incidents,
    monitors,
    organizations,
    ping_logs,
    users,
)
from app.core.config import settings
from app.core.errors import AppError
from app.worker.broker import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Sentinel API...")

    if not broker.is_worker_process:
        await broker.startup()
        print("Taskiq/Redis connection established successfully.")

    yield

    print("Shutting down Sentinel API...")
    if not broker.is_worker_process:
        await broker.shutdown()
        print("Taskiq/Redis connection closed successfully.")


middleware = [
    Middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type]
        allow_origins=["*"],  # Change this to specific domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

# Init FastAPI app
app = FastAPI(
    title=settings.project_name,
    description=settings.description,
    version=settings.version,
    middleware=middleware,
)

# Include API routes
app.include_router(alert_channels.router, prefix="/api/v1/alert-channels")
app.include_router(api_keys.router, prefix="/api/v1/api-keys")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(daily_stats.router, prefix="/api/v1/daily-stats")
app.include_router(hourly_stats.router, prefix="/api/v1/hourly-stats")
app.include_router(incidents.router, prefix="/api/v1/incidents")
app.include_router(monitors.router, prefix="/api/v1/monitors")
app.include_router(organizations.router, prefix="/api/v1/organizations")
app.include_router(ping_logs.router, prefix="/api/v1/ping-logs")
app.include_router(users.router, prefix="/api/v1/users")


# Global exception handler for AppError
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.message)},
        headers={"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None,
    )


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "online",
        "service": settings.project_name,
        "version": settings.version,
    }
