"""
Narrative Nexus - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.exceptions import (
    generic_exception_handler,
    validation_exception_handler,
)
from app.memory import MemoryManager

logger = get_logger(__name__)

# Global memory manager
memory_manager = MemoryManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    logger.info("Starting Narrative Nexus", version=settings.APP_VERSION)
    
    try:
        await memory_manager.initialize()
        logger.info("Memory system initialized")
    except Exception as e:
        logger.error("Failed to initialize memory system", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Narrative Nexus")
    await memory_manager.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered collaborative story writing platform",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(Exception, validation_exception_handler)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "memory_system": "initialized" if memory_manager._initialized else "not_initialized",
    }


# Import and include routers
from app.api.stories import router as stories_router
from app.api.websocket import router as websocket_router

app.include_router(stories_router, prefix="/api/v1/stories", tags=["stories"])
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])
