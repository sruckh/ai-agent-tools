import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
import sys
from loguru import logger

from api_server.auth_middleware import auth_middleware
from api_server.v1_utils_router import v1_utils_router
from api_server.v1_media_router import v1_media_api_router
from video.config import device

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | <blue>{extra}</blue>",
    level="DEBUG",
)

logger.info("This server was created by the 'AI Agents A-Z' YouTube channel")
logger.info("https://www.youtube.com/@aiagentsaz")
logger.info("Using device: {}", device)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the server...")
    yield
    logger.info("Shutting down the server...")

app = FastAPI(lifespan=lifespan)


# add middleware to app, besides the /health endpoint
app.middleware("http")(auth_middleware)

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {
        "message": "Welcome to the AI Agents A-Z No-Code Server",
        "version": "0.3.5",
        "documentation": "/docs",
        "created_by": "https://www.youtube.com/@aiagentsaz"
    }

@app.api_route("/health", methods=["GET", "HEAD"])
def healthcheck():
    return {"status": "ok"}

api_router = APIRouter()
v1_api_router = APIRouter()

# =============================================================================
# RunPod Handler Implementation
# =============================================================================

# Save the following content to a new file: runpod_base.py
"""
RunPod Base Handler Classes and Utilities

This module provides the base classes and utilities for RunPod serverless handlers.
It includes common functionality like error handling, logging, storage operations,
and response formatting.
"""

# Embedded handler code removed - using unified runpod_handler.py instead

# Include routers for API functionality
v1_api_router.include_router(v1_media_api_router, prefix="/v1/media")
v1_api_router.include_router(v1_utils_router, prefix="/v1/utils")
api_router.include_router(v1_api_router, prefix="/api")
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)