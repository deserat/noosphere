# API Service Context (Python/FastAPI)

This file provides context for AI coding assistants working on the Noosphere API service. It defines service boundaries, responsibilities, patterns, and API contracts.

## Service Overview

**Purpose**: Backend API service providing REST endpoints, AI classification, and background scheduling.

**Technology Stack**:
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL 14+ with pgvector extension
- **ORM**: SQLAlchemy 2.0+ (async support)
- **Migrations**: Alembic
- **AI**: litellm (multi-provider AI integration)
- **Scheduler**: APScheduler (background jobs)
- **Validation**: Pydantic v2 models

**Port**: 8000 (default, configurable via environment)

## Service Boundaries

### Responsibilities

**This Service DOES**:
- ✅ Provide REST API for CRUD operations on items
- ✅ AI-powered classification using litellm (Gemini/Claude/GPT)
- ✅ Generate vector embeddings for semantic search
- ✅ Background scheduling for surfacing jobs
- ✅ Database schema management (Alembic migrations)
- ✅ Health check endpoints for monitoring
- ✅ Markdown file utilities (parse/write frontmatter)

**This Service DOES NOT**:
- ❌ Watch file system for vault changes (sync-service responsibility)
- ❌ Provide TUI or CLI interface (CLI responsibility)
- ❌ Store markdown files (vault is file-based)
- ❌ Handle user authentication UI (CLI responsibility)

### Dependencies

**External Services**:
- PostgreSQL database
- AI API providers (Gemini, OpenAI, Anthropic)
- File vault at `~/noosphere-vault` (optional, for development)

**Consumed By**:
- CLI (Rust): Calls REST API endpoints
- Sync Service (Rust): Triggers API updates on file changes

## Directory Structure

```
api-service/
├── app/                      # Main application package
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API layer
│   │   └── endpoints/       # Route handlers
│   │       ├── health.py    # Health check endpoints
│   │       └── items.py     # Item CRUD endpoints
│   ├── core/                # Core utilities
│   │   ├── config.py        # Configuration management
│   │   └── security.py      # Security utilities (Phase 2+)
│   ├── db/                  # Database layer
│   │   ├── base.py          # SQLAlchemy base class
│   │   └── session.py       # Database session management
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── item.py          # Item model
│   │   ├── tag.py           # Tag model
│   │   └── ...              # Other models
│   ├── schemas/             # Pydantic request/response models
│   │   ├── item.py          # Item schemas
│   │   └── ...              # Other schemas
│   ├── crud/                # Database operations
│   │   ├── item.py          # Item CRUD operations
│   │   └── ...              # Other CRUD modules
│   ├── services/            # Business logic
│   │   ├── ai.py            # AI classification service
│   │   ├── scheduler.py     # Background scheduler
│   │   └── surfacing.py     # Surfacing logic (Phase 3)
│   └── vault/               # Markdown utilities
│       ├── parser.py        # YAML frontmatter parser
│       ├── writer.py        # Markdown file writer
│       └── template.py      # Markdown templates
├── migrations/              # Alembic database migrations
│   ├── env.py              # Alembic environment
│   └── versions/           # Migration files
├── tests/                   # Pytest test suite
│   ├── api/                # API endpoint tests
│   ├── crud/               # CRUD operation tests
│   └── services/           # Service logic tests
├── config.yaml             # Service configuration
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not committed)
```

## API Contracts

### REST API Endpoints

Base URL: `http://localhost:8000/api`

#### Health Check

```
GET /api/health
Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:00:00Z",
  "database": "connected",
  "scheduler": "running",
  "version": "0.1.0"
}
```

```
GET /api/health/ready
Response: 200 OK (service ready) | 503 Service Unavailable
{
  "status": "ready" | "not ready",
  "reason": "..." (if not ready)
}
```

```
GET /api/health/live
Response: 200 OK
{
  "status": "alive"
}
```

#### Items CRUD

```
GET /api/items
Query Parameters:
  - category: string (optional)
  - tags: string[] (optional)
  - limit: int (default: 50)
  - offset: int (default: 0)

Response: 200 OK
[
  {
    "id": "uuid",
    "title": "string",
    "content": "string",
    "category": "ideas" | "tasks" | "notes" | "resources" | "journal",
    "tags": ["tag1", "tag2"],
    "created_at": "datetime",
    "updated_at": "datetime",
    "surfaced_at": "datetime",
    "next_surface": "datetime",
    "cadence": "daily" | "weekly" | "monthly" | null
  }
]
```

```
GET /api/items/{id}
Response: 200 OK | 404 Not Found
{
  "id": "uuid",
  "title": "string",
  "content": "string",
  ...
}
```

```
POST /api/items
Request Body:
{
  "title": "string",
  "content": "string",
  "category": "ideas",
  "tags": ["tag1", "tag2"]
}

Response: 201 Created
{
  "id": "uuid",
  ...
}
```

```
PUT /api/items/{id}
Request Body: (all fields optional)
{
  "title": "string",
  "content": "string",
  "tags": ["tag1", "tag2"]
}

Response: 200 OK | 404 Not Found
```

```
DELETE /api/items/{id}
Response: 204 No Content | 404 Not Found
```

#### AI Classification (Phase 2)

```
POST /api/items/{id}/classify
Request Body:
{
  "model": "gemini-1.5-flash" (optional)
}

Response: 200 OK
{
  "category": "ideas",
  "tags": ["productivity", "automation"],
  "confidence": 0.87
}
```

#### Semantic Search (Phase 2)

```
GET /api/items/search
Query Parameters:
  - query: string (required)
  - limit: int (default: 10)

Response: 200 OK
[
  {
    "item": { ... },
    "similarity": 0.92
  }
]
```

## Configuration

### Environment Variables

Required:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/noosphere
```

Optional:
```bash
# Vault path (for development/testing)
VAULT_PATH=~/noosphere-vault

# AI API keys
GEMINI_API_KEY=your-key
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key

# API server
API_HOST=127.0.0.1
API_PORT=8000

# Logging
LOG_LEVEL=INFO

# Database pool
DB_POOL_SIZE=5
```

### Configuration File

`config.yaml`:
```yaml
database:
  url: postgresql://localhost/noosphere
  pool_size: 5
  echo: false

api:
  host: 127.0.0.1
  port: 8000
  reload: true  # Development only

ai:
  classification:
    model: gemini-1.5-flash
    temperature: 0.3
  embedding:
    model: text-embedding-004
    dimension: 768

scheduler:
  enabled: true
  surfacing_interval: 300    # 5 minutes
  cleanup_interval: 3600     # 1 hour

logging:
  level: INFO
  format: "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
```

## Database Schema

### Key Tables

**items**:
- `id`: UUID (primary key)
- `title`: VARCHAR(500)
- `content`: TEXT
- `category`: VARCHAR(50)
- `tags`: VARCHAR[] (array)
- `embedding`: VECTOR(768) (pgvector)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP
- `surfaced_at`: TIMESTAMP (nullable)
- `next_surface`: TIMESTAMP (nullable)
- `cadence`: VARCHAR(20) (nullable)

**tags**:
- `id`: UUID
- `name`: VARCHAR(50)
- `count`: INTEGER

**item_tags** (junction table):
- `item_id`: UUID (foreign key)
- `tag_id`: UUID (foreign key)

See [`docs/project/stories/EPIC-2-2-database-models-migrations.md`](../docs/project/stories/EPIC-2-2-database-models-migrations.md) for complete schema.

## Patterns and Conventions

### FastAPI Endpoint Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.item import ItemCreate, ItemResponse
from app.crud.item import item_crud

router = APIRouter()

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db)
) -> ItemResponse:
    """Create new item."""
    item = item_crud.create(db, obj_in=item_in)
    return item
```

### CRUD Pattern

```python
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

class ItemCRUD:
    def get(self, db: Session, id: str) -> Optional[Item]:
        return db.query(Item).filter(Item.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Item]:
        return db.query(Item).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ItemCreate) -> Item:
        item = Item(**obj_in.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(
        self,
        db: Session,
        *,
        db_obj: Item,
        obj_in: ItemUpdate
    ) -> Item:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

item_crud = ItemCRUD()
```

### AI Classification Pattern

```python
import litellm
from app.core.config import get_config

async def classify_item(item: Item) -> dict:
    config = get_config()
    model = config.ai["classification"]["model"]

    prompt = f"""
    Classify this item into one of: ideas, tasks, notes, resources, journal
    Extract relevant tags.

    Title: {item.title}
    Content: {item.content}

    Return JSON: {{"category": "...", "tags": [...]}}
    """

    response = await litellm.acompletion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result = response.choices[0].message.content
    return json.loads(result)
```

### Error Handling Pattern

```python
from fastapi import HTTPException, status

class ItemNotFoundError(HTTPException):
    def __init__(self, item_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )

# Usage
item = item_crud.get(db, id=item_id)
if not item:
    raise ItemNotFoundError(item_id)
```

## Testing Patterns

### Endpoint Testing

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    response = client.post(
        "/api/items",
        json={
            "title": "Test item",
            "content": "Test content",
            "category": "ideas"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test item"
    assert "id" in data
```

### Database Testing

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.item import Item

@pytest.fixture
def db_session():
    engine = create_engine("postgresql://test:test@localhost/noosphere_test")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_item(db_session):
    item = Item(title="Test", content="Content", category="ideas")
    db_session.add(item)
    db_session.commit()

    assert item.id is not None
    assert item.created_at is not None
```

## Development Workflow

### Running Locally

```bash
cd api-service

# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head

# Start development server (auto-reload)
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Creating Migrations

```bash
# After modifying models
alembic revision --autogenerate -m "Add new field to items"

# Review generated migration in migrations/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/api/test_items.py

# Specific test
pytest tests/api/test_items.py::test_create_item
```

## Common Tasks

### Adding New Endpoint

1. Create Pydantic schema in `app/schemas/`
2. Create CRUD operations in `app/crud/`
3. Create endpoint in `app/api/endpoints/`
4. Register router in `app/main.py`
5. Write tests in `tests/api/`

### Adding AI Feature

1. Implement service logic in `app/services/ai.py`
2. Create endpoint to trigger AI operation
3. Handle errors gracefully (API quota, timeouts)
4. Add tests with mocked AI responses

### Adding Background Job

1. Define job function in `app/services/scheduler.py`
2. Add job to scheduler configuration
3. Test job execution independently
4. Monitor job logs

## Integration Points

### With CLI

CLI calls API endpoints for:
- Creating items (POST /api/items)
- Fetching items (GET /api/items)
- Searching items (GET /api/items/search)
- Getting surfaced items (GET /api/items/surface)

### With Sync Service

Sync service calls API for:
- Creating items from vault files (POST /api/items)
- Updating items when files change (PUT /api/items/{id})
- Deleting items when files removed (DELETE /api/items/{id})

API notifies sync service via:
- (Future) Webhook for database changes
- (Current) Sync service polls for changes

## Security Considerations

### Phase 1 (Local Development)

- No authentication required (localhost only)
- Database credentials in environment variables
- AI API keys in environment variables

### Phase 2+ (Production)

- JWT authentication for API endpoints
- HTTPS for all API communication
- API rate limiting
- Input validation (Pydantic handles this)
- SQL injection prevention (SQLAlchemy handles this)

## Performance Considerations

### Database Optimization

- Indexes on frequently queried columns (category, tags, created_at)
- Connection pooling (SQLAlchemy)
- Async database operations (asyncpg)
- Pagination for large result sets

### AI Operation Optimization

- Cache AI responses (Phase 2+)
- Batch processing for multiple items
- Timeouts for AI API calls
- Fallback to simpler classification if AI fails

### API Performance

- Async endpoints for I/O operations
- Response compression (gzip)
- CORS configuration for frontend
- Health check caching (don't query DB every time)

## Troubleshooting

### Database Connection Errors

```
Error: "could not connect to server"
Fix: Check PostgreSQL is running, verify DATABASE_URL
```

### Migration Errors

```
Error: "can't locate revision"
Fix: alembic stamp head (if starting fresh)
```

### AI API Errors

```
Error: "API key not found"
Fix: Set GEMINI_API_KEY or OPENAI_API_KEY in .env
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [litellm Documentation](https://docs.litellm.ai)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

## Next Steps

When working on this service:

1. Read [`docs/agents/architecture.md`](../docs/agents/architecture.md) for system architecture
2. Read [`docs/agents/standards.md`](../docs/agents/standards.md) for coding standards
3. Check [`docs/project/stories/`](../docs/project/stories/) for current user stories
4. Focus on Phase 1 stories first (EPIC-2, EPIC-4, EPIC-5)
