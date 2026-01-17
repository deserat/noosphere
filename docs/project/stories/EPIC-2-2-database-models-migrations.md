# SQLAlchemy Models and Migration System

**Epic**: Database Foundation
**Priority**: P1
**Story Points**: 13

## User Story

As a developer,
I need complete SQLAlchemy ORM models and a migration system,
So that the database schema is version-controlled, reproducible, and supports all Noosphere features including AI vector search.

## Acceptance Criteria

### Model Infrastructure
- [ ] `api-service/app/models/__init__.py` created (exports all models)
- [ ] `api-service/app/db/base.py` created with declarative base:
  ```python
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import DeclarativeBase

  Base = declarative_base()
  # Or for SQLAlchemy 2.0+:
  class Base(DeclarativeBase):
      pass
  ```

### Core Table Models (9 models total)
- [ ] **User Model** (`api-service/app/models/user.py`):
  - Fields: id (UUID), email (unique), created, settings (JSONB)
  - Indexes: email
- [ ] **User Config Model** (`api-service/app/models/user_config.py`):
  - Fields: user_id (FK), key, value (JSONB)
  - Primary key: (user_id, key)
- [ ] **Item Model** (`api-service/app/models/item.py`):
  - Fields:
    - Identity: id (UUID), title, file_path (unique)
    - Classification: category, subcategory, tags (array)
    - State: state (enum)
    - Timestamps: created, modified, last_worked, categorized_at
    - Surfacing: next_surface, cadence
    - AI: confidence, embedding (vector), embedding_updated
    - Sync: content_hash, no_ai (boolean)
    - Multi-tenant: user_id (FK)
  - Indexes: category, state, next_surface, tags (GIN), embedding (ivfflat/hnsw)
  - Full-text search: search_vector (tsvector)
  - Constraints: valid_confidence CHECK
- [ ] **Item Links Model** (`api-service/app/models/item_link.py`):
  - Fields: id (UUID), from_item_id (FK), to_item_id (FK), link_type, why_related, confidence, created
  - Unique constraint: (from_item_id, to_item_id, link_type)
  - Check constraint: no_self_links
  - Indexes: from_item_id, to_item_id
- [ ] **Conversation Model** (`api-service/app/models/conversation.py`):
  - Fields: id (UUID), item_id (FK), session_start, session_end, user_id (FK)
  - RRD-style: full_transcript (JSONB), detailed_summary, brief_summary, key_outcomes
  - Metadata: detail_level, last_summarized, changes_made (JSONB)
  - Indexes: item_id, user_id, session_start
- [ ] **Prompt Model** (`api-service/app/models/prompt.py`):
  - Fields: id (UUID), name (unique), version, content, model_config (JSONB), active, created
  - Unique constraint: (name, version)
- [ ] **Token Usage Model** (`api-service/app/models/token_usage.py`):
  - Fields: id (UUID), user_id (FK), operation, model, input_tokens, output_tokens, cost_usd, timestamp
  - Indexes: user_id, timestamp
- [ ] **Audit Log Model** (`api-service/app/models/audit_log.py`):
  - Fields: id (UUID), user_id (FK), item_id (FK, nullable), action, before (JSONB), after (JSONB), timestamp
  - Indexes: user_id, item_id, timestamp

### Alembic Migration Setup
- [ ] Alembic initialized in `api-service/migrations/`:
  ```bash
  cd api-service
  alembic init migrations
  ```
- [ ] `alembic.ini` configured with database connection:
  ```ini
  sqlalchemy.url = postgresql://noosphere_user:dev_password@localhost:5432/noosphere
  ```
  - Better: Use environment variable:
  ```python
  sqlalchemy.url = driver://user:pass@localhost/dbname
  # Will be replaced at runtime by env var
  ```
- [ ] `migrations/env.py` configured to:
  - Load all models from `app/models/`
  - Import Base from `app/db/base`
  - Use Base.metadata for autogenerate
  - Support environment variable for database URL
- [ ] Initial migration generated from models:
  ```bash
  alembic revision --autogenerate -m "Initial schema"
  ```
- [ ] Migration applied successfully:
  ```bash
  alembic upgrade head
  ```
- [ ] All tables created with correct schema:
  - 9 tables total
  - All indexes created
  - All foreign keys set up
  - All constraints applied

### Verification Queries
- [ ] Tables exist and are queryable:
  ```sql
  \dt  -- List tables
  \d items  -- Describe items table
  ```
- [ ] Indexes created correctly:
  ```sql
  \di  -- List indexes
  ```
- [ ] Vector column works:
  ```python
  # Test pgvector column
  from sqlalchemy import create_engine, select
  from src.models.item import Item

  engine = create_engine(DATABASE_URL)
  with engine.connect() as conn:
      # Insert test item with embedding
      stmt = insert(Item).values(
          title='Test',
          embedding='[0.1, 0.2, 0.3, ...]'  # 1536 dimensions
      )
      result = conn.execute(stmt)
      conn.commit()
  ```

## Technical Notes

**SQLAlchemy 2.0 Features**:
- Use `DeclarativeBase` instead of `declarative_base()`
- Use `Mapped[type]` for type hints
- Use `mapped_column()` instead of `Column()`
- Example:
  ```python
  from sqlalchemy.orm import Mapped, mapped_column

  class User(Base):
      __tablename__ = "users"

      id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
      email: Mapped[str] = mapped_column(unique=True, nullable=False)
  ```

**pgvector Integration**:
- Use pgvector SQLAlchemy extension:
  ```python
  from pgvector.sqlalchemy import Vector

  embedding = Column(Vector(1536))  # 1536 for OpenAI embeddings
  ```
- Indexes for fast similarity search:
  ```python
  # Add in migration or model
  Index('idx_items_embedding', 'embedding',
        postgresql_using='ivfflat',
        postgresql_ops={'embedding': 'vector_cosine_ops'})
  ```

**Enum Types**:
- Define Python enums for state, category:
  ```python
  from enum import Enum as PyEnum
  from sqlalchemy import Enum

  class ItemState(str, PyEnum):
      UNCATEGORIZED = "uncategorized"
      NOT_STARTED = "not-started"
      IN_PROGRESS = "in-progress"
      COMPLETED = "completed"
      ARCHIVED = "archived"

  state = Column(Enum(ItemState), nullable=False)
  ```

**Migration Best Practices**:
- Always review autogenerated migrations before applying
- Add meaningful migration messages
- Test migrations on development database first
- Keep migrations small and focused
- Document complex schema changes

**Rollback Strategy**:
```bash
# Check current version
alembic current

# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>

# Rollback all
alembic downgrade base
```

## Dependencies

- **Blocks**:
  - EPIC-2-3 (Database connection needs models to query)
  - EPIC-5-1 (API service needs models for business logic)
- **Blocked By**:
  - EPIC-1-1 (Repository structure needed for migrations directory)
  - EPIC-1-2 (Python environment needed for SQLAlchemy)
  - EPIC-2-1 (Database must exist)
- **Related**:
  - EPIC-3-1 (Vault utilities will use Item model)

## Verification

### Model Import Test
```bash
cd api-service
source venv/bin/activate

python -c "
from app.models import User, Item, ItemLink, Conversation
from app.models import Prompt, TokenUsage, AuditLog, UserConfig
from app.db.base import Base

print(f'Base metadata tables: {len(Base.metadata.tables)}')
# Should print: Base metadata tables: 9

for table_name in Base.metadata.tables.keys():
    print(f'✓ {table_name}')
"
```

### Database Schema Verification
```sql
-- Connect to database
psql -U noosphere_user -d noosphere

-- Check all tables exist
\dt

-- Expected tables:
-- users, user_config, items, item_links, conversations,
-- prompts, token_usage, audit_log, alembic_version

-- Check items table structure
\d items

-- Should show:
-- - id (uuid)
-- - title (text)
-- - embedding (vector)
-- - All other fields
-- - All indexes
-- - All constraints

-- Check indexes
\di

-- Should include:
-- - idx_items_category
-- - idx_items_state
-- - idx_items_embedding
-- - idx_items_tags (GIN)
-- - etc.
```

### Migration Verification
```bash
cd api-service

# Check current migration
alembic current
# Should show latest migration hash

# Check migration history
alembic history
# Should show all migrations

# Test rollback
alembic downgrade -1
# Should rollback successfully

# Test upgrade
alembic upgrade head
# Should upgrade back to latest

# Verify tables still exist after rollback/upgrade cycle
```

### Vector Column Test
```bash
python -c "
from sqlalchemy import create_engine, insert, select
from app.models.item import Item
import os

engine = create_engine(os.getenv('DATABASE_URL'))

# Test vector insertion
with engine.begin() as conn:
    # Insert item with embedding
    stmt = insert(Item).values(
        title='Vector Test',
        file_path='test/vector.md',
        category='Ideas',
        embedding=[0.1] * 1536  # 1536-dimensional vector
    )
    result = conn.execute(stmt)

    # Query back
    stmt = select(Item).where(Item.title == 'Vector Test')
    item = conn.execute(stmt).first()

    assert len(item.embedding) == 1536
    print('✓ Vector column working')

    # Cleanup
    conn.execute('DELETE FROM items WHERE title = \"Vector Test\"')
"
```

**Completion Criteria**:
- [ ] All 9 model files created and importable
- [ ] Alembic configured and initial migration generated
- [ ] `alembic upgrade head` creates all tables successfully
- [ ] All tables, indexes, and constraints exist in database
- [ ] pgvector column works for embeddings
- [ ] Models can be imported and used in Python
- [ ] Migration can be rolled back and re-applied without errors
- [ ] Database schema matches information architecture specification
