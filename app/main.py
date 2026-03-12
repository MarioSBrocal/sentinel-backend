from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, monitors, users

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
    title="Sentinel Monitoring API",
    description="Backend engine for Sentinel SaaS",
    version="0.1.0",
    middleware=middleware,
)

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(monitors.router, prefix="/api/v1/monitors")
app.include_router(users.router, prefix="/api/v1/users")


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "online", "service": "sentinel-api", "version": "0.1.0"}
