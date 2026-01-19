# EPIC-1-10: SQLAlchemy Models and Migration System

## Issue Reference
- **GitHub Issue**: #10
- **Epic**: EPIC-1 (Database Foundation)
- **Priority**: P1 (Core foundation)
- **Story Points**: 13
- **Service**: api-service

## Feature Summary

Create complete SQLAlchemy ORM models and Alembic migration system for the Noosphere API service. This establishes the database schema foundation including 9 core tables with support for AI vector embeddings (pgvector), full-text search, and multi-tenant architecture.

## Current State (from exploration)

✓ `app/db/base.py` exists with `DeclarativeBase` already set up
✓ `app/models/` directory exists (empty, ready for models)
✓ Alembic fully initialized and configured in `alembic/`
✓ pgvector dependency present in requirements.txt (`pgvector>=0.2.4`)
✓ DATABASE_URL configured in `.env`
✓ PostgreSQL with pgvector extension set up (EPIC-1-9)

## Implementation Plan

### Phase 1: Independent Models (No Foreign Keys)

#### File: `api-service/app/models/user.py`
**Purpose:** Base entity for multi-tenancy

**Fields:**
- `id`: UUID (primary key, auto-generated)
- `email`: String (unique, indexed, required)
- `created`: DateTime (auto timestamp)
- `settings`: JSONB (nullable, for user preferences)

**Indexes:**
- `email` (B-tree, for fast lookups)

**Rationale:** Foundation table for multi-tenant architecture. No dependencies on other models.

---

#### File: `api-service/app/models/prompt.py`
**Purpose:** AI prompt template management

**Fields:**
- `id`: UUID (primary key, auto-generated)
- `name`: String (required)
- `version`: String (required)
- `content`: Text (prompt template)
- `model_config`: JSONB (AI model settings)
- `active`: Boolean (default True)
- `created`: DateTime (auto timestamp)

**Constraints:**
- UNIQUE constraint on (`name`, `version`) - prevent duplicate versions

**Rationale:** Independent entity for managing AI classification prompts.

---

### Phase 2: Simple Dependencies

#### File: `api-service/app/models/user_config.py`
**Purpose:** Key-value storage for user-specific configuration

**Fields:**
- `user_id`: UUID (FK → users.id, part of composite PK)
- `key`: String (part of composite PK)
- `value`: JSONB (configuration value)

**Primary Key:** Composite (`user_id`, `key`)

**Foreign Keys:**
- `user_id` → `users.id` (CASCADE delete)

**Rationale:** Flexible user settings storage with composite primary key pattern.

---

#### File: `api-service/app/models/item.py` ⭐ **MOST COMPLEX**
**Purpose:** Core entity representing knowledge items in the vault

**Identity Fields:**
- `id`: UUID (primary key, auto-generated)
- `title`: String (required, max 500 chars)
- `file_path`: String (unique, required)

**Classification Fields:**
- `category`: String (indexed)
- `subcategory`: String (nullable)
- `tags`: ARRAY(String) (GIN indexed for fast array operations)

**State Management:**
- `state`: Enum (uncategorized, not-started, in-progress, completed, archived)

**Timestamp Fields:**
- `created`: DateTime (auto timestamp)
- `modified`: DateTime (auto timestamp, auto-update)
- `last_worked`: DateTime (nullable)
- `categorized_at`: DateTime (nullable)

**Surfacing Fields:**
- `next_surface`: DateTime (nullable, indexed)
- `cadence`: String (nullable, e.g., "daily", "weekly")

**AI Fields:**
- `confidence`: Float (CHECK constraint: BETWEEN 0 AND 1)
- `embedding`: Vector(1536) (pgvector, indexed for similarity search)
- `embedding_updated`: DateTime (nullable)

**Sync Fields:**
- `content_hash`: String (for change detection)
- `no_ai`: Boolean (default False, opt-out of AI processing)

**Multi-tenant:**
- `user_id`: UUID (FK → users.id, required)

**Full-text Search:**
- `search_vector`: TSVECTOR (auto-populated via PostgreSQL trigger)

**Indexes:**
- `category` (B-tree)
- `state` (B-tree)
- `next_surface` (B-tree)
- `tags` (GIN for array operations)
- `embedding` (Vector index for similarity search)
- `search_vector` (GIN for full-text search)
- `user_id` (B-tree, for multi-tenant queries)

**Constraints:**
- UNIQUE: `file_path`
- CHECK: `confidence >= 0 AND confidence <= 1`
- FK: `user_id` → `users.id` (CASCADE)

**Special Features:**
- PostgreSQL trigger to auto-populate `search_vector` from `title` and content
- Vector similarity search support via pgvector

**Rationale:** Most complex model with pgvector integration, full-text search, and comprehensive metadata.

---

#### File: `api-service/app/models/token_usage.py`
**Purpose:** Track AI API token consumption and costs

**Fields:**
- `id`: UUID (primary key, auto-generated)
- `user_id`: UUID (FK → users.id, required)
- `operation`: String (e.g., "classification", "embedding")
- `model`: String (e.g., "gpt-4", "text-embedding-ada-002")
- `input_tokens`: Integer
- `output_tokens`: Integer
- `cost_usd`: Numeric(10, 6) (precise decimal for cost)
- `timestamp`: DateTime (auto timestamp, indexed)

**Indexes:**
- `user_id` (B-tree, for per-user analytics)
- `timestamp` (B-tree, for time-series queries)

**Foreign Keys:**
- `user_id` → `users.id` (CASCADE)

**Rationale:** Cost tracking and usage analytics for AI operations.

---

### Phase 3: Complex Dependencies

#### File: `api-service/app/models/item_link.py`
**Purpose:** Graph relationships between items

**Fields:**
- `id`: UUID (primary key, auto-generated)
- `from_item_id`: UUID (FK → items.id, required, indexed)
- `to_item_id`: UUID (FK → items.id, required, indexed)
- `link_type`: String (e.g., "related", "references", "depends-on")
- `why_related`: Text (explanation of relationship)
- `confidence`: Float (0-1, from AI analysis)
- `created`: DateTime (auto timestamp)

**Constraints:**
- UNIQUE: (`from_item_id`, `to_item_id`, `link_type`)
- CHECK: `from_item_id != to_item_id` (no self-links)

**Indexes:**
- `from_item_id` (B-tree, for outgoing links)
- `to_item_id` (B-tree, for incoming links)

**Foreign Keys:**
- `from_item_id` → `items.id` (CASCADE)
- `to_item_id` → `items.id` (CASCADE)

**Rationale:** Enables knowledge graph features and relationship discovery.

---

#### File: `api-service/app/models/conversation.py`
**Purpose:** Track AI conversations about items (RRD pattern)

**Fields:**
- `id`: UUID (primary key, auto-generated)
- `item_id`: UUID (FK → items.id, required, indexed)
- `user_id`: UUID (FK → users.id, required, indexed)
- `session_start`: DateTime (indexed)
- `session_end`: DateTime (nullable)

**RRD-style Fields (Retain, Reduce, Discard):**
- `full_transcript`: JSONB (complete conversation, retained temporarily)
- `detailed_summary`: Text (reduced form for medium-term retention)
- `brief_summary`: Text (minimal summary for long-term retention)
- `key_outcomes`: Text (permanent distilled insights)

**Metadata Fields:**
- `detail_level`: String (current retention level: "full", "detailed", "brief")
- `last_summarized`: DateTime (when last reduction occurred)
- `changes_made`: JSONB (what edits resulted from conversation)

**Indexes:**
- `item_id` (B-tree, conversations about an item)
- `user_id` (B-tree, user's conversation history)
- `session_start` (B-tree, chronological queries)

**Foreign Keys:**
- `item_id` → `items.id` (CASCADE)
- `user_id` → `users.id` (CASCADE)

**Rationale:** Implements RRD pattern for conversation retention with progressive summarization.

---

#### File: `api-service/app/models/audit_log.py`
**Purpose:** Comprehensive audit trail for all system changes

**Fields:**
- `id`: UUID (primary key, auto-generated)
- `user_id`: UUID (FK → users.id, required, indexed)
- `item_id`: UUID (FK → items.id, nullable, indexed)
- `action`: String (e.g., "create", "update", "delete", "classify")
- `before`: JSONB (state before change, nullable)
- `after`: JSONB (state after change, nullable)
- `timestamp`: DateTime (auto timestamp, indexed)

**Indexes:**
- `user_id` (B-tree, user activity tracking)
- `item_id` (B-tree, item change history)
- `timestamp` (B-tree, chronological queries)

**Foreign Keys:**
- `user_id` → `users.id` (CASCADE)
- `item_id` → `items.id` (SET NULL) - preserve audit even if item deleted

**Rationale:** Complete audit trail for compliance and debugging. item_id nullable to preserve logs after item deletion.

---

### Phase 4: Infrastructure

#### File: `api-service/app/models/__init__.py`
**Purpose:** Clean model export interface

**Contents:**
```python
"""
SQLAlchemy ORM models for Noosphere API service.
"""
from app.models.user import User
from app.models.user_config import UserConfig
from app.models.item import Item
from app.models.item_link import ItemLink
from app.models.conversation import Conversation
from app.models.prompt import Prompt
from app.models.token_usage import TokenUsage
from app.models.audit_log import AuditLog

__all__ = [
    "User",
    "UserConfig",
    "Item",
    "ItemLink",
    "Conversation",
    "Prompt",
    "TokenUsage",
    "AuditLog",
]
```

---

#### Modify: `api-service/app/db/base.py`
**Purpose:** Import all models for Alembic autogenerate discovery

**Add imports:**
```python
# Import all models here for Alembic autogenerate discovery
from app.models.user import User
from app.models.user_config import UserConfig
from app.models.item import Item
from app.models.item_link import ItemLink
from app.models.conversation import Conversation
from app.models.prompt import Prompt
from app.models.token_usage import TokenUsage
from app.models.audit_log import AuditLog
```

**Rationale:** Alembic's autogenerate needs all models imported so they're in Base.metadata.

---

## Architecture Decisions

### 1. SQLAlchemy 2.0 Patterns
**Decision:** Use modern SQLAlchemy 2.0 syntax exclusively

**Implementation:**
- Use `DeclarativeBase` class (already in base.py)
- Use `Mapped[type]` type hints for all columns
- Use `mapped_column()` instead of `Column()`
- Use relationship() with explicit type hints

**Example:**
```python
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    created: Mapped[datetime] = mapped_column(default=func.now())
```

**Rationale:** Modern syntax provides better type safety and IDE support.

---

### 2. pgvector Integration
**Decision:** Use Vector(1536) for OpenAI embeddings

**Implementation:**
```python
from pgvector.sqlalchemy import Vector

embedding: Mapped[Vector] = mapped_column(Vector(1536), nullable=True)
```

**Index Strategy:**
- Initial migration: Create basic index on embedding column
- Future migration: Add specialized ivfflat or hnsw index after data population
- ivfflat/hnsw require tuning parameters and existing data

**Rationale:**
- 1536 dimensions matches OpenAI's text-embedding-ada-002 model
- Basic index sufficient for initial deployment
- Specialized vector indexes optimized later with real data

---

### 3. PostgreSQL-Specific Types

**ARRAY for tags:**
```python
from sqlalchemy import ARRAY, String

tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
```

**JSONB for settings/metadata:**
```python
from sqlalchemy.dialects.postgresql import JSONB

settings: Mapped[dict] = mapped_column(JSONB, nullable=True)
```

**TSVECTOR for full-text search:**
```python
from sqlalchemy.dialects.postgresql import TSVECTOR

search_vector: Mapped[str] = mapped_column(TSVECTOR, nullable=True)
```

**PostgreSQL Trigger for search_vector (Option A - Approved):**
```sql
-- Created in Alembic migration
CREATE OR REPLACE FUNCTION items_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        COALESCE(NEW.title, '') || ' ' ||
        COALESCE(NEW.category, '') || ' ' ||
        array_to_string(COALESCE(NEW.tags, ARRAY[]::text[]), ' ')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER items_search_vector_trigger
    BEFORE INSERT OR UPDATE ON items
    FOR EACH ROW EXECUTE FUNCTION items_search_vector_update();
```

**Rationale:** Use PostgreSQL's native types for optimal performance.

---

### 4. Enum Handling
**Decision:** Use Python str enums with SQLAlchemy Enum type

**Implementation:**
```python
from enum import Enum as PyEnum
from sqlalchemy import Enum

class ItemState(str, PyEnum):
    UNCATEGORIZED = "uncategorized"
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Item(Base):
    state: Mapped[ItemState] = mapped_column(
        Enum(ItemState, name="item_state"),
        nullable=False,
        default=ItemState.UNCATEGORIZED
    )
```

**Rationale:** Type-safe enums in Python with PostgreSQL ENUM constraint.

---

### 5. Primary Keys
**Decision:** UUID for all tables (except composite PKs)

**Implementation:**
```python
import uuid
from sqlalchemy.dialects.postgresql import UUID

id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
)
```

**Rationale:** UUIDs prevent ID collision, enable distributed systems, and obscure record counts.

---

### 6. Timestamps
**Decision:** Auto-managed timestamps with database defaults

**Implementation:**
```python
from sqlalchemy import func

created: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
modified: Mapped[datetime] = mapped_column(
    default=func.now(),
    onupdate=func.now(),
    nullable=False
)
```

**Rationale:** Database-managed timestamps ensure consistency.

---

### 7. Foreign Key Cascade Rules

**CASCADE delete (multi-tenant cleanup):**
- `user_id` in all tables (when user deleted, remove all their data)
- `item_id` in item_links, conversations (when item deleted, clean up relationships)

**SET NULL (preserve audit trail):**
- `audit_log.item_id` (preserve logs even after item deletion)

**Implementation:**
```python
from sqlalchemy import ForeignKey

user_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
    index=True
)

# For audit logs
item_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("items.id", ondelete="SET NULL"),
    nullable=True,
    index=True
)
```

**Rationale:** Automatic cleanup while preserving audit integrity.

---

## Database Changes

### New Tables (9 total)

1. **users** - User accounts and multi-tenancy
2. **user_config** - User-specific configuration (composite PK)
3. **items** - Core knowledge items with vector embeddings
4. **item_links** - Graph relationships between items
5. **conversations** - AI conversation history (RRD pattern)
6. **prompts** - AI prompt templates
7. **token_usage** - AI API usage tracking
8. **audit_log** - Complete audit trail
9. **alembic_version** - Alembic migration tracking (auto-created)

### Indexes Summary

**B-tree indexes (fast equality/range queries):**
- users: email
- items: category, state, next_surface, user_id, file_path (via UNIQUE)
- item_links: from_item_id, to_item_id
- conversations: item_id, user_id, session_start
- token_usage: user_id, timestamp
- audit_log: user_id, item_id, timestamp

**GIN indexes (array and full-text search):**
- items: tags (array operations)
- items: search_vector (full-text search)

**Vector indexes (similarity search):**
- items: embedding (basic index initially)

### Constraints Summary

**PRIMARY KEY:** All tables have primary key
- UUID for most tables
- Composite (user_id, key) for user_config

**UNIQUE:**
- users.email
- items.file_path
- prompts.(name, version)
- item_links.(from_item_id, to_item_id, link_type)

**CHECK:**
- items.confidence >= 0 AND confidence <= 1
- item_links.from_item_id != to_item_id

**FOREIGN KEY:**
- All user_id → users.id (CASCADE)
- item_id → items.id (CASCADE or SET NULL for audit_log)
- from_item_id, to_item_id → items.id (CASCADE)

---

## Migration Strategy

### Step 1: Create all model files
Order: User → Prompt → UserConfig → Item → TokenUsage → ItemLink → Conversation → AuditLog

### Step 2: Create `app/models/__init__.py`
Export all 8 models for clean imports

### Step 3: Update `app/db/base.py`
Import all models for Alembic autogenerate discovery

### Step 4: Generate migration
```bash
cd api-service
uv run alembic revision --autogenerate -m "Initial schema with 9 tables"
```

### Step 5: Review generated migration
Manual inspection:
- ✓ All 9 tables created (users, user_config, items, item_links, conversations, prompts, token_usage, audit_log, alembic_version)
- ✓ All columns with correct types
- ✓ All indexes created
- ✓ All constraints (UNIQUE, CHECK, FK) created
- ✓ pgvector Vector type used correctly
- ✓ PostgreSQL-specific types (ARRAY, JSONB, TSVECTOR) used correctly

### Step 6: Add search_vector trigger to migration
Manually add SQL for tsvector trigger (Alembic won't autogenerate this):
```python
# In upgrade()
op.execute("""
    CREATE OR REPLACE FUNCTION items_search_vector_update() RETURNS trigger AS $$
    BEGIN
        NEW.search_vector := to_tsvector('english',
            COALESCE(NEW.title, '') || ' ' ||
            COALESCE(NEW.category, '') || ' ' ||
            array_to_string(COALESCE(NEW.tags, ARRAY[]::text[]), ' ')
        );
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER items_search_vector_trigger
        BEFORE INSERT OR UPDATE ON items
        FOR EACH ROW EXECUTE FUNCTION items_search_vector_update();
""")

# In downgrade()
op.execute("DROP TRIGGER IF EXISTS items_search_vector_trigger ON items;")
op.execute("DROP FUNCTION IF EXISTS items_search_vector_update();")
```

### Step 7: Apply migration
```bash
uv run alembic upgrade head
```

### Step 8: Verify schema
```bash
# Connect to database
psql -U noosphere_user -d noosphere

# List tables (expect 9)
\dt

# Inspect items table structure
\d items

# List all indexes
\di

# Check constraints
\d+ items
```

### Step 9: Test vector insertion
```python
# Simple Python test
from sqlalchemy import create_engine
from app.models import Item
import os

engine = create_engine(os.getenv('DATABASE_URL'))
with engine.begin() as conn:
    # Insert test item with 1536-dim vector
    stmt = insert(Item).values(
        title='Vector Test',
        file_path='test/vector.md',
        category='test',
        user_id='<test-user-uuid>',
        embedding=[0.1] * 1536  # 1536 dimensions
    )
    conn.execute(stmt)

    # Query back
    result = conn.execute(select(Item).where(Item.title == 'Vector Test'))
    item = result.first()
    assert len(item.embedding) == 1536
    print("✓ Vector column works")

    # Cleanup
    conn.execute(delete(Item).where(Item.title == 'Vector Test'))
```

### Step 10: Test rollback
```bash
# Test migration is reversible
uv run alembic downgrade -1

# Verify tables dropped
psql -U noosphere_user -d noosphere -c "\dt"

# Upgrade again
uv run alembic upgrade head

# Verify tables recreated
psql -U noosphere_user -d noosphere -c "\dt"
```

---

## Testing Strategy

### Unit Tests (models)
**Location:** `api-service/tests/models/`

**Test files to create:**
- `test_user.py` - User model instantiation, validation
- `test_item.py` - Item model with vector, arrays, constraints
- `test_item_link.py` - Link validation, no-self-link constraint
- `test_conversation.py` - RRD fields, relationships
- `test_enums.py` - Enum value validation

**Coverage target:** 90%+ of model code

**Example test:**
```python
import pytest
from app.models import Item, User

def test_item_confidence_validation():
    """Test that confidence CHECK constraint works"""
    user = User(email="test@example.com")

    # Valid confidence
    item = Item(
        title="Test",
        file_path="test.md",
        user_id=user.id,
        confidence=0.85
    )
    assert item.confidence == 0.85

    # Invalid confidence would fail at database level (tested in integration)
```

### Integration Tests (database)
**Note:** Integration tests are co-located with unit tests in `api-service/tests/models/` for convenience. Each model test file contains both unit tests (model instantiation, validation) and integration tests (database constraints, triggers, relationships).

**Coverage target:** Critical paths covered

**Example test:**
```python
import pytest
from sqlalchemy import create_engine, text
from app.db.base import Base

@pytest.fixture
def db_engine():
    engine = create_engine(os.getenv('DATABASE_URL'))
    yield engine
    engine.dispose()

def test_all_tables_created(db_engine):
    """Verify all 9 tables exist"""
    with db_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        count = result.scalar()
        assert count == 9, f"Expected 9 tables, found {count}"

def test_vector_similarity_search(db_engine):
    """Test pgvector similarity search works"""
    with db_engine.begin() as conn:
        # Insert test items with embeddings
        conn.execute(text("""
            INSERT INTO items (title, file_path, user_id, embedding)
            VALUES ('Test 1', 'test1.md', :user_id, :embedding)
        """), {
            'user_id': str(test_user_id),
            'embedding': [0.1] * 1536
        })

        # Test similarity search
        result = conn.execute(text("""
            SELECT title, embedding <-> :query::vector AS distance
            FROM items
            ORDER BY distance
            LIMIT 1
        """), {'query': [0.1] * 1536})

        row = result.first()
        assert row.title == 'Test 1'
        assert row.distance < 0.1  # Very similar
```

---

## Verification Steps

### 1. Database Schema Verification
```sql
-- Connect to database
psql -U noosphere_user -d noosphere

-- Check table count
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public';
-- Expected: 9 tables

-- List all tables
\dt
-- Expected: users, user_config, items, item_links, conversations, prompts, token_usage, audit_log, alembic_version

-- Inspect items table (most complex)
\d items
-- Verify all columns, types, indexes, constraints

-- Check all indexes
SELECT indexname, tablename, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Check all constraints
SELECT
    conname AS constraint_name,
    contype AS constraint_type,
    conrelid::regclass AS table_name
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace
ORDER BY conrelid::regclass::text;
```

### 2. pgvector Verification
```sql
-- Verify pgvector extension enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Test vector operations
SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector AS distance;
-- Should return Euclidean distance

-- Check items.embedding column type
SELECT column_name, data_type, udt_name
FROM information_schema.columns
WHERE table_name = 'items' AND column_name = 'embedding';
-- Expected: udt_name = 'vector'
```

### 3. Full-text Search Verification
```sql
-- Check trigger exists
SELECT tgname, tgrelid::regclass, proname
FROM pg_trigger t
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE tgrelid = 'items'::regclass;
-- Expected: items_search_vector_trigger

-- Test trigger functionality
INSERT INTO items (title, file_path, category, tags, user_id)
VALUES ('Test Item', 'test.md', 'ideas', ARRAY['test', 'demo'], '<user-uuid>');

SELECT title, search_vector
FROM items
WHERE title = 'Test Item';
-- Verify search_vector is populated

-- Test full-text search
SELECT title
FROM items
WHERE search_vector @@ to_tsquery('english', 'test');
-- Should return 'Test Item'

-- Cleanup
DELETE FROM items WHERE title = 'Test Item';
```

### 4. Migration Verification
```bash
# Check current migration version
cd api-service
uv run alembic current

# View migration history
uv run alembic history

# Test downgrade
uv run alembic downgrade -1
psql -U noosphere_user -d noosphere -c "\dt"  # Should show no tables (except alembic_version)

# Test upgrade
uv run alembic upgrade head
psql -U noosphere_user -d noosphere -c "\dt"  # Should show all 9 tables

# Verify repeatability
uv run alembic downgrade base
uv run alembic upgrade head
# Should succeed without errors
```

---

## Rollback Strategy

If issues discovered during verification:

```bash
# Rollback migration
uv run alembic downgrade -1

# Or rollback completely
uv run alembic downgrade base

# Fix models or migration file

# Regenerate migration if needed
uv run alembic revision --autogenerate -m "Initial schema (fixed)"

# Reapply
uv run alembic upgrade head
```

---

## Success Criteria

### Functional Requirements
- [ ] All 9 model files created and importable
- [ ] All models use SQLAlchemy 2.0 syntax (Mapped, mapped_column)
- [ ] pgvector Vector(1536) column works in Item model
- [ ] PostgreSQL trigger auto-populates search_vector
- [ ] All relationships (FKs) properly defined
- [ ] All indexes created (B-tree, GIN, Vector)
- [ ] All constraints enforced (UNIQUE, CHECK, FK)
- [ ] Alembic migration generated and applied successfully
- [ ] Migration is reversible (downgrade/upgrade works)

### Quality Requirements
- [ ] Ruff format passes
- [ ] Ruff check passes
- [ ] Pyright type checking passes
- [ ] Unit tests for models (90%+ coverage)
- [ ] Integration tests for database operations
- [ ] All tests pass

### Verification Requirements
- [ ] Database schema matches specification
- [ ] Vector similarity search works
- [ ] Full-text search works
- [ ] FK cascade behavior correct
- [ ] CHECK constraints enforce rules
- [ ] Documentation updated (if needed)

---

## Dependencies

**Blocked By:**
- EPIC-1-1: Repository structure ✓ (completed)
- EPIC-1-2: Python environment with uv ✓ (completed)
- EPIC-2-1: PostgreSQL database setup ✓ (completed)
- EPIC-1-9: PostgreSQL with pgvector ✓ (completed)

**Blocks:**
- EPIC-2-3: Database connection session management
- EPIC-5-1: API service endpoints (needs models)
- EPIC-3-1: Vault utilities (needs Item model)

---

## Notes

- **Vector index optimization**: Initial migration creates basic index. Specialized ivfflat/hnsw indexes will be added in later migration after data population.
- **Async SQLAlchemy**: Models are compatible with async sessions (will be implemented in EPIC-2-3).
- **Full-text search**: Using PostgreSQL trigger approach for auto-population (Option A).
- **Enum strategy**: Using Python enums with SQLAlchemy Enum type for type safety.
- **Testing approach**: Unit tests for model logic, integration tests for database functionality.
