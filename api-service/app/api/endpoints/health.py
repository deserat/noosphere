"""Health check endpoints for monitoring and probes.

Provides three endpoints:
- /health - Detailed health status
- /health/ready - Readiness probe (Kubernetes)
- /health/live - Liveness probe (Kubernetes)
"""

from fastapi import APIRouter
from pydantic import BaseModel

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
    overall_status = "healthy" if db_healthy and scheduler_status == "running" else "degraded"

    response = HealthResponse(
        status=overall_status,
        database=db_healthy,
        scheduler=scheduler_status,
        version="0.1.0",
    )

    # Return 503 if any component is unhealthy
    if not db_healthy or scheduler_status != "running":
        return response

    return response


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

    if not db_healthy:
        return ReadyResponse(ready=False)

    return ReadyResponse(ready=True)


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
