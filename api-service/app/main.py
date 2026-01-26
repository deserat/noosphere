"""Noosphere API Service - FastAPI application entry point.

This module creates the FastAPI application with modern lifespan events,
health check endpoints, and placeholder item routes.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import health, items
from app.core.config import get_config, load_config
from app.db.session import connect_with_retry
from app.services.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup and shutdown events.

    Startup sequence:
    1. Load configuration
    2. Connect to database (fail fast)
    3. Start scheduler (fail fast if enabled)

    Shutdown sequence:
    1. Stop scheduler gracefully

    Args:
        app: FastAPI application instance

    Yields:
        None - application runs between startup and shutdown
    """
    # ========== STARTUP ==========
    logger.info("Starting Noosphere API service...")

    # 1. Load configuration
    try:
        config = load_config("config.yaml")
        logger.info(f"Configuration loaded: {config.api['host']}:{config.api['port']}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    # 2. Connect to database (fail fast)
    try:
        connect_with_retry()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    # 3. Start scheduler (fail fast if enabled)
    if config.scheduler.get("enabled", True):
        try:
            start_scheduler()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    else:
        logger.info("Scheduler disabled in configuration")

    logger.info("Startup complete - API service ready")

    yield  # Application runs here

    # ========== SHUTDOWN ==========
    logger.info("Shutting down Noosphere API service...")
    stop_scheduler()
    logger.info("Shutdown complete")


# Create FastAPI application with lifespan
app = FastAPI(
    title="Noosphere API",
    description="Knowledge management system with spaced repetition and AI classification",
    version="0.1.0",
    lifespan=lifespan,
)

# Load configuration for middleware setup (with fallback for tests)
try:
    config = get_config()
    cors_origins = config.api.get("cors_origins", ["http://localhost:3000"])
    api_prefix = config.api.get("api_prefix", "/api")
    api_version = config.api.get("api_version", "v1")
except RuntimeError:
    # Config not loaded yet (e.g., during test imports) - use defaults
    cors_origins = ["http://localhost:3000"]
    api_prefix = "/api"
    api_version = "v1"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register health endpoints (no version prefix - standard path)
app.include_router(health.router, prefix="/health", tags=["health"])

# Register items endpoints (with API version prefix)
app.include_router(
    items.router,
    prefix=f"{api_prefix}/{api_version}/items",
    tags=["items"],
)


@app.get("/", tags=["root"])
async def root():
    """API root endpoint.

    Returns service information and links to documentation.

    Returns:
        dict: Service metadata and navigation links
    """
    return {
        "service": "Noosphere API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "api": f"{api_prefix}/{api_version}",
    }
