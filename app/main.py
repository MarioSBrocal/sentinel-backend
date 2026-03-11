from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth

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


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "online", "service": "sentinel-api", "version": "0.1.0"}
