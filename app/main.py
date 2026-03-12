from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import alert_channels, auth, monitors, users
from app.core.config import settings

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
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(monitors.router, prefix="/api/v1/monitors")
app.include_router(users.router, prefix="/api/v1/users")


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "online",
        "service": settings.project_name,
        "version": settings.version,
    }
