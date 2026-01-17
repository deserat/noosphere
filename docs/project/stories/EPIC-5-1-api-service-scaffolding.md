# FastAPI Service with Health Check and Scheduler

**Epic**: Service Scaffolding
**Priority**: P1
**Story Points**: 8

## User Story

As a developer,
I need a minimal but functional FastAPI service with health check endpoint and integrated background scheduler,
So that I can verify the service architecture and begin implementing business logic.

## Acceptance Criteria

### FastAPI Application Setup
- [ ] `api-service/app/main.py` created with FastAPI application:
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  import uvicorn
  import logging
  from contextlib import asynccontextmanager

  from app.core.config import load_config, get_config
  from app.db.session import check_database_health
  from app.services.scheduler import scheduler

  # Configure logging
  logging.basicConfig(
      level=logging.INFO,
      format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
  )
  logger = logging.getLogger(__name__)

  @asynccontextmanager
  async def lifespan(app: FastAPI):
      """Handle startup and shutdown events."""
      # Startup
      logger.info("Starting Noosphere API service...")

      # Load configuration
      load_config("config.yaml")
      config = get_config()

      # Verify database connection
      if not check_database_health():
          logger.error("Database health check failed")
          raise RuntimeError("Cannot connect to database")

      logger.info("Database connection verified")

      # Start background scheduler if enabled
      if config.scheduler.get("enabled", False):
          scheduler.start()
          logger.info("Background scheduler started")

      yield

      # Shutdown
      logger.info("Shutting down Noosphere API service...")
      if scheduler.running:
          scheduler.shutdown()
          logger.info("Background scheduler stopped")

  # Create FastAPI application
  app = FastAPI(
      title="Noosphere API",
      description="Personal knowledge management API with AI capabilities",
      version="0.1.0",
      lifespan=lifespan
  )

  # Configure CORS
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],  # Frontend dev server
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

  # Import routers
  from app.api.endpoints.health import router as health_router
  from app.api.endpoints.items import router as items_router

  # Register routers
  app.include_router(health_router, prefix="/api", tags=["health"])
  app.include_router(items_router, prefix="/api/items", tags=["items"])

  if __name__ == "__main__":
      config = get_config()
      uvicorn.run(
          "app.main:app",
          host=config.api["host"],
          port=config.api["port"],
          reload=config.api.get("reload", False),
          log_level="info"
      )
  ```

### Health Check Endpoint
- [ ] `api-service/app/api/endpoints/health.py` created with health check route:
  ```python
  from fastapi import APIRouter, status
  from pydantic import BaseModel
  from datetime import datetime

  from app.db.session import check_database_health
  from app.core.config import get_config

  router = APIRouter()

  class HealthResponse(BaseModel):
      status: str
      timestamp: datetime
      database: str
      scheduler: str
      version: str

  @router.get("/health", response_model=HealthResponse)
  async def health_check():
      """Health check endpoint for service monitoring."""
      from app.services.scheduler import scheduler

      return HealthResponse(
          status="healthy",
          timestamp=datetime.utcnow(),
          database="connected" if check_database_health() else "disconnected",
          scheduler="running" if scheduler.running else "stopped",
          version="0.1.0"
      )

  @router.get("/health/ready")
  async def readiness_check():
      """Readiness check for Kubernetes/container orchestration."""
      if not check_database_health():
          return {"status": "not ready", "reason": "database unavailable"}, 503

      return {"status": "ready"}

  @router.get("/health/live")
  async def liveness_check():
      """Liveness check for Kubernetes/container orchestration."""
      return {"status": "alive"}
  ```

### Items API Router (Placeholder)
- [ ] `api-service/app/api/endpoints/items.py` created with placeholder routes:
  ```python
  from fastapi import APIRouter, HTTPException, status
  from pydantic import BaseModel
  from typing import List, Optional
  from datetime import datetime
  import uuid

  router = APIRouter()

  class ItemResponse(BaseModel):
      id: str
      title: str
      category: str
      created: datetime

  @router.get("/", response_model=List[ItemResponse])
  async def list_items(
      category: Optional[str] = None,
      limit: int = 50,
      offset: int = 0
  ):
      """List items (placeholder - returns empty list)."""
      # TODO: Implement actual database query
      return []

  @router.get("/{item_id}", response_model=ItemResponse)
  async def get_item(item_id: str):
      """Get single item by ID (placeholder)."""
      # TODO: Implement actual database query
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=f"Item {item_id} not found"
      )

  @router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
  async def create_item(title: str, category: str):
      """Create new item (placeholder)."""
      # TODO: Implement actual item creation
      return ItemResponse(
          id=str(uuid.uuid4()),
          title=title,
          category=category,
          created=datetime.utcnow()
      )
  ```

### Background Scheduler
- [ ] `api-service/app/services/scheduler.py` created with APScheduler integration:
  ```python
  from apscheduler.schedulers.background import BackgroundScheduler
  from apscheduler.triggers.interval import IntervalTrigger
  import logging

  from app.core.config import get_config

  logger = logging.getLogger(__name__)

  # Global scheduler instance
  scheduler = BackgroundScheduler()

  def surfacing_job():
      """Background job for surfacing items based on cadence."""
      logger.info("Running surfacing job...")
      # TODO: Implement actual surfacing logic
      # 1. Query items where next_surface <= now
      # 2. Use AI to generate surfacing prompt
      # 3. Update next_surface based on cadence
      logger.info("Surfacing job completed")

  def cleanup_job():
      """Background job for cleanup tasks."""
      logger.info("Running cleanup job...")
      # TODO: Implement actual cleanup logic
      # 1. Remove stale lock files
      # 2. Clean up old audit logs
      # 3. Vacuum database if needed
      logger.info("Cleanup job completed")

  def configure_scheduler():
      """Configure scheduled jobs based on config."""
      config = get_config()
      scheduler_config = config.scheduler

      # Add surfacing job
      surfacing_interval = scheduler_config.get("surfacing_interval", 300)  # 5 minutes default
      scheduler.add_job(
          surfacing_job,
          trigger=IntervalTrigger(seconds=surfacing_interval),
          id="surfacing_job",
          name="Surface items based on cadence",
          replace_existing=True
      )
      logger.info(f"Surfacing job scheduled every {surfacing_interval} seconds")

      # Add cleanup job
      cleanup_interval = scheduler_config.get("cleanup_interval", 3600)  # 1 hour default
      scheduler.add_job(
          cleanup_job,
          trigger=IntervalTrigger(seconds=cleanup_interval),
          id="cleanup_job",
          name="Cleanup stale resources",
          replace_existing=True
      )
      logger.info(f"Cleanup job scheduled every {cleanup_interval} seconds")

  # Configure jobs when module is imported
  try:
      configure_scheduler()
  except Exception as e:
      logger.warning(f"Could not configure scheduler: {e}")
  ```

### Service Startup Script
- [ ] `api-service/run.sh` created for development:
  ```bash
  #!/bin/bash
  set -e

  echo "Starting Noosphere API Service..."

  # Activate virtual environment
  source venv/bin/activate

  # Run database migrations
  echo "Running database migrations..."
  alembic upgrade head

  # Start service
  echo "Starting FastAPI server..."
  python -m app.main
  ```
- [ ] Script made executable: `chmod +x api-service/run.sh`

### Dependencies Installation
- [ ] APScheduler added to requirements.txt:
  ```
  APScheduler==3.10.4
  ```
- [ ] Dependencies installed:
  ```bash
  cd api-service
  pip install -r requirements.txt
  ```

### Service Verification
- [ ] Service starts successfully: `./run.sh`
- [ ] Health check responds: `curl http://localhost:8000/api/health`
- [ ] API documentation accessible: `http://localhost:8000/docs`
- [ ] Background scheduler starts and runs jobs
- [ ] Database connection verified at startup
- [ ] Service shuts down gracefully (Ctrl+C)

## Technical Notes

**FastAPI Lifespan Events**:
- Modern approach using `@asynccontextmanager` (replaces deprecated `@app.on_event`)
- Startup: Load config, verify database, start scheduler
- Shutdown: Stop scheduler, cleanup resources

**APScheduler vs. Celery**:
- APScheduler: In-process, simple, sufficient for Phase 1
- Celery: Separate worker process, more complex, better for production scale
- Decision: Start with APScheduler (simpler), migrate to Celery if needed

**CORS Configuration**:
- Development: Allow localhost:3000 (future frontend dev server)
- Production: Restrict to actual frontend domain
- Never use allow_origins=["*"] in production

**Health Check Patterns**:
- `/health`: General health status with component details
- `/health/ready`: Readiness probe (is service ready to accept traffic?)
- `/health/live`: Liveness probe (is service process alive?)
- Kubernetes-compatible endpoints

**Background Scheduler Jobs**:
1. **Surfacing Job**: Query items, run AI surfacing logic, update next_surface
2. **Cleanup Job**: Remove stale locks, prune old logs, database maintenance

**Service Startup Order**:
1. Load configuration from config.yaml + environment variables
2. Verify database connection (fail fast if unavailable)
3. Run database migrations (ensure schema is up to date)
4. Start background scheduler (if enabled in config)
5. Start FastAPI server (uvicorn)

**Development vs Production**:
```python
# Development
uvicorn.run("app.main:app", reload=True, workers=1)

# Production
uvicorn.run("app.main:app", reload=False, workers=4)
# Or use gunicorn with uvicorn workers:
# gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4
```

**Placeholder Endpoints**:
- Items router has placeholder implementations
- Returns empty lists or 404 errors
- Allows testing of service infrastructure
- Will be implemented in Phase 2 (AI Classification)

**Error Handling Strategy**:
- Fail fast at startup (database connection, config validation)
- Graceful degradation at runtime (log errors, return 503 if needed)
- Background jobs: Log errors but don't crash service

## Dependencies

- **Blocks**:
  - Phase 2 stories (API service must exist for AI classification)
- **Blocked By**:
  - EPIC-1-2 (Python environment needed)
  - EPIC-2-2 (Database models needed for queries)
  - EPIC-2-3 (Database connection module needed)
  - EPIC-4-2 (Configuration loader needed)
- **Related**:
  - EPIC-5-2 (Sync service will call API endpoints)
  - EPIC-5-3 (Startup script will launch this service)

## Verification

### Service Startup Test
```bash
cd api-service

# Start service
./run.sh

# Expected output:
# Starting Noosphere API Service...
# Running database migrations...
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# [2024-01-15 10:00:00] INFO - app.main - Starting Noosphere API service...
# [2024-01-15 10:00:00] INFO - app.main - Database connection verified
# [2024-01-15 10:00:00] INFO - app.services.scheduler - Surfacing job scheduled every 300 seconds
# [2024-01-15 10:00:00] INFO - app.services.scheduler - Cleanup job scheduled every 3600 seconds
# [2024-01-15 10:00:00] INFO - app.main - Background scheduler started
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Health Check Test
```bash
# Test health endpoint
curl http://localhost:8000/api/health | jq

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:00:00.000000",
#   "database": "connected",
#   "scheduler": "running",
#   "version": "0.1.0"
# }

# Test readiness endpoint
curl http://localhost:8000/api/health/ready

# Expected: {"status": "ready"}

# Test liveness endpoint
curl http://localhost:8000/api/health/live

# Expected: {"status": "alive"}
```

### API Documentation Test
```bash
# Open browser to API docs
xdg-open http://localhost:8000/docs

# Should show:
# - Swagger UI with all endpoints
# - Health check endpoints
# - Items endpoints (placeholder)
# - Request/response schemas
# - Try it out functionality
```

### Placeholder Endpoints Test
```bash
# Test list items (should return empty array)
curl http://localhost:8000/api/items/ | jq
# Expected: []

# Test get item (should return 404)
curl http://localhost:8000/api/items/test-id
# Expected: {"detail": "Item test-id not found"}

# Test create item (should return placeholder response)
curl -X POST "http://localhost:8000/api/items/?title=Test&category=Ideas" | jq
# Expected: {"id": "...", "title": "Test", "category": "Ideas", "created": "..."}
```

### Scheduler Test
```bash
# Start service and watch logs
./run.sh

# Wait 5 minutes (surfacing interval)
# Expected log output every 300 seconds:
# [2024-01-15 10:05:00] INFO - app.services.scheduler - Running surfacing job...
# [2024-01-15 10:05:00] INFO - app.services.scheduler - Surfacing job completed

# Wait 1 hour (cleanup interval)
# Expected log output every 3600 seconds:
# [2024-01-15 11:00:00] INFO - app.services.scheduler - Running cleanup job...
# [2024-01-15 11:00:00] INFO - app.services.scheduler - Cleanup job completed
```

### Graceful Shutdown Test
```bash
# Start service
./run.sh

# Press Ctrl+C

# Expected output:
# ^C
# INFO:     Shutting down
# [2024-01-15 10:00:00] INFO - app.main - Shutting down Noosphere API service...
# [2024-01-15 10:00:00] INFO - app.main - Background scheduler stopped
# INFO:     Finished server process [12345]

# Verify clean shutdown (no error messages, scheduler stopped)
```

**Completion Criteria**:
- [ ] FastAPI application created with lifespan management
- [ ] Health check endpoints respond correctly
- [ ] Database connection verified at startup
- [ ] Background scheduler starts and runs jobs on schedule
- [ ] API documentation accessible at /docs
- [ ] Placeholder item endpoints return appropriate responses
- [ ] Service starts successfully with ./run.sh script
- [ ] Service shuts down gracefully without errors
- [ ] CORS configured for frontend development
- [ ] Logging configured and working
