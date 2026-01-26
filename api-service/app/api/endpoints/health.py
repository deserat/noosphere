"""Health check endpoints for monitoring and probes.

Provides three endpoints:
- /health - Detailed health status
- /health/ready - Readiness probe (Kubernetes)
- /health/live - Liveness probe (Kubernetes)
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import __version__
from app.db.session import check_database_health
from app.services.scheduler import get_scheduler_status

router = APIRouter()


class HealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    database: bool
    scheduler: str
    version: str


class ReadyResponse(BaseModel):
    """Readiness probe response."""

    ready: bool


class LiveResponse(BaseModel):
    """Liveness probe response."""

    alive: bool


@router.get("/", response_model=HealthResponse)
async def health():
    """Detailed health check endpoint.

    Returns comprehensive health status of all components.
    Returns 503 if any component is unhealthy.

    Returns:
        HealthResponse: Detailed status of database, scheduler, and service
    """
    db_healthy = check_database_health()
    scheduler_status = get_scheduler_status()

    # Determine overall status
    is_healthy = db_healthy and scheduler_status == "running"
    overall_status = "healthy" if is_healthy else "degraded"

    response_data = {
        "status": overall_status,
        "database": db_healthy,
        "scheduler": scheduler_status,
        "version": __version__,
    }

    # Return 503 if any component is unhealthy
    if not is_healthy:
        return JSONResponse(status_code=503, content=response_data)

    return response_data


@router.get(
    "/ready",
    response_model=ReadyResponse,
    responses={
        200: {"description": "Service is ready"},
        503: {"description": "Service not ready"},
    },
)
async def ready():
    """Readiness probe endpoint for Kubernetes.

    Checks if the service is ready to handle requests.
    Load balancers use this to decide if instance should receive traffic.

    Returns:
        ReadyResponse: Readiness status
    """
    # Check database connection - critical for readiness
    db_healthy = check_database_health()

    response_data = {"ready": db_healthy}

    if not db_healthy:
        return JSONResponse(status_code=503, content=response_data)

    return response_data


@router.get(
    "/live",
    response_model=LiveResponse,
    responses={200: {"description": "Service is alive"}},
)
async def live():
    """Liveness probe endpoint for Kubernetes.

    Always returns 200 OK if the process is running.
    Kubernetes uses this to decide if the pod should be restarted.

    Returns:
        LiveResponse: Always returns alive=True
    """
    return LiveResponse(alive=True)
