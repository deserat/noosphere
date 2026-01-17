# Database Connection Module and Seed Data

**Epic**: Database Foundation
**Priority**: P1
**Story Points**: 5

## User Story

As a developer,
I need a robust database connection module with session management and seed data,
So that the application can reliably interact with the database and developers can test with realistic data.

## Acceptance Criteria

### Database Connection Module
- [ ] `api-service/app/db/session.py` created with:
  - Connection pooling configuration
  - Session factory
  - Session management utilities
  - Health check function
  - Connection retry logic with exponential backoff
- [ ] Connection pool configured with sensible defaults:
  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from sqlalchemy.pool import QueuePool

  engine = create_engine(
      DATABASE_URL,
      poolclass=QueuePool,
      pool_size=5,  # Number of connections to maintain
      max_overflow=10,  # Additional connections if pool exhausted
      pool_pre_ping=True,  # Verify connections before use
      pool_recycle=3600,  # Recycle connections after 1 hour
      echo=False  # Set to True for SQL query logging (development)
  )

  SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
  ```
- [ ] Session context manager implemented:
  ```python
  from contextlib import contextmanager

  @contextmanager
  def get_db_session():
      session = SessionLocal()
      try:
          yield session
          session.commit()
      except Exception:
          session.rollback()
          raise
      finally:
          session.close()
  ```
- [ ] Health check function:
  ```python
  def check_database_health() -> bool:
      try:
          with get_db_session() as session:
              session.execute('SELECT 1')
          return True
      except Exception as e:
          logger.error(f"Database health check failed: {e}")
          return False
  ```
- [ ] Connection retry logic with exponential backoff:
  ```python
  import time
  from tenacity import retry, stop_after_attempt, wait_exponential

  @retry(
      stop=stop_after_attempt(5),
      wait=wait_exponential(multiplier=1, min=1, max=10)
  )
  def connect_with_retry():
      engine.connect()
  ```
- [ ] Usage patterns documented in docstrings and `docs/database.md`:
  - When to use `get_db_session()`
  - How to handle transactions
  - Best practices for connection management
  - Avoiding common pitfalls (session leaks, etc.)

### Seed Data Script
- [ ] `api-service/migrations/seed_data.py` created with:
  - Seed user creation (single MVP user)
  - Sample prompts (classification prompt v1)
  - Sample items in each category
  - Embedding placeholders (zeros for now, will be generated in Phase 6)
- [ ] Seed user:
  ```python
  user = User(
      id=uuid.uuid4(),
      email="dev@noosphere.local",
      created=datetime.utcnow(),
      settings={}
  )
  ```
- [ ] Classification prompt (v1):
  ```python
  prompt = Prompt(
      name="classification",
      version=1,
      content="""Analyze this captured item and classify it...
      [Full prompt content]
      Return JSON: {category, subcategory, tags, confidence}""",
      model_config={"temperature": 0.3, "model": "gemini-1.5-flash"},
      active=True
  )
  ```
- [ ] Sample items created (at least one per category):
  ```python
  items = [
      Item(title="Call dentist", category="Admin", subcategory="Tasks", ...),
      Item(title="Blog post idea", category="Ideas", subcategory="Creative", ...),
      Item(title="Meeting with Sarah", category="People", subcategory="Colleagues", ...),
      Item(title="Website redesign", category="Projects", subcategory="Work", ...),
  ]
  ```
- [ ] Embedding placeholders (zeros):
  ```python
  for item in items:
      item.embedding = [0.0] * 1536  # Will be replaced with real embeddings
      item.embedding_updated = None
  ```
- [ ] Script is idempotent (can be run multiple times without duplicating data):
  ```python
  # Check if seed user already exists
  existing_user = session.query(User).filter_by(email="dev@noosphere.local").first()
  if existing_user:
      print("Seed user already exists, skipping...")
      return
  ```
- [ ] Documentation on how to run seed script:
  ```bash
  cd api-service
  python migrations/seed_data.py
  ```

### Environment Variable Support
- [ ] Database URL loaded from environment:
  ```python
  import os
  from dotenv import load_dotenv

  load_dotenv()
  DATABASE_URL = os.getenv("DATABASE_URL")

  if not DATABASE_URL:
      raise ValueError("DATABASE_URL environment variable not set")
  ```
- [ ] Fallback to default for development (documented but not in code for security)

## Technical Notes

**Connection Pooling Benefits**:
- Reuses connections instead of creating new ones for each request
- Reduces overhead of connection establishment
- Limits total connections to avoid overwhelming database
- Pre-ping ensures stale connections are refreshed

**Session Management Best Practices**:
- Always use context managers (`with get_db_session()`)
- Never share sessions between requests/threads
- Close sessions explicitly in finally blocks
- Commit explicitly after successful operations
- Rollback on exceptions

**Seed Data Design**:
- Representative of real data but clearly marked as test data
- Email uses `.local` TLD to indicate non-production
- Diverse examples across all categories
- Enough data to test UI and workflows
- Not too much data (keep it minimal for Phase 1)

**Retry Logic Rationale**:
- Database might not be ready immediately on startup
- Network issues can cause transient failures
- Exponential backoff prevents overwhelming database
- Finite retry attempts prevent infinite loops

**Transaction Isolation**:
- Default: READ COMMITTED (PostgreSQL default)
- Sufficient for most operations
- Can be changed per-session if needed:
  ```python
  session = SessionLocal()
  session.connection(execution_options={"isolation_level": "SERIALIZABLE"})
  ```

**Common Pitfalls to Avoid**:
1. **Session Leaks**: Always close sessions
2. **Long Transactions**: Keep transactions short
3. **N+1 Queries**: Use eager loading with joinedload()
4. **Stale Data**: Refresh objects after external changes
5. **Connection Pool Exhaustion**: Monitor pool metrics

## Dependencies

- **Blocks**:
  - EPIC-5-1 (API service needs database connection for health check)
- **Blocked By**:
  - EPIC-1-2 (Python environment needed)
  - EPIC-2-1 (Database must exist)
  - EPIC-2-2 (Models needed for seed data)
- **Related**:
  - EPIC-4-2 (Config loader will load DATABASE_URL)

## Verification

### Connection Module Test
```bash
cd api-service
source venv/bin/activate

python -c "
from app.db.session import (
    engine,
    SessionLocal,
    get_db_session,
    check_database_health,
    connect_with_retry
)

# Test connection
connect_with_retry()
print('✓ Connection established with retry')

# Test health check
assert check_database_health() == True
print('✓ Health check passed')

# Test session management
with get_db_session() as session:
    result = session.execute('SELECT 1').scalar()
    assert result == 1
print('✓ Session management working')

# Test pool statistics
pool = engine.pool
print(f'Pool size: {pool.size()}')
print(f'Checked out connections: {pool.checkedout()}')
print('✓ Connection pool configured')
"
```

### Seed Data Test
```bash
cd api-service

# Run seed script
python migrations/seed_data.py

# Expected output:
# Creating seed user...
# Creating classification prompt...
# Creating sample items...
# Seed data created successfully

# Verify data in database
psql -U noosphere_user -d noosphere -c "
  SELECT
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM prompts) as prompts,
    (SELECT COUNT(*) FROM items) as items;
"

# Should show at least:
# users | prompts | items
# ------+---------+-------
#     1 |       1 |     4

# Verify user
psql -U noosphere_user -d noosphere -c "
  SELECT id, email, created FROM users;
"

# Should show dev@noosphere.local

# Verify items span all categories
psql -U noosphere_user -d noosphere -c "
  SELECT category, COUNT(*) FROM items GROUP BY category;
"

# Should show items in: Admin, Ideas, People, Projects
```

### Idempotency Test
```bash
# Run seed script twice
python migrations/seed_data.py
python migrations/seed_data.py

# Expected output on second run:
# Seed user already exists, skipping...
# (or similar idempotent behavior)

# Verify no duplicates
psql -U noosphere_user -d noosphere -c "
  SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
"

# Should return no rows (no duplicates)
```

### Connection Retry Test
```python
# Test retry logic
from app.db.session import connect_with_retry
import pytest

# Temporarily stop PostgreSQL
# sudo systemctl stop postgresql

try:
    connect_with_retry()
except Exception as e:
    print(f"✓ Retry logic attempted connection: {e}")

# Restart PostgreSQL
# sudo systemctl start postgresql

# Should succeed after restart
connect_with_retry()
print("✓ Connection successful after database restart")
```

**Completion Criteria**:
- [ ] Database connection module created with all required functions
- [ ] Connection pooling configured and working
- [ ] Health check function returns True for healthy database
- [ ] Session context manager works correctly (commit on success, rollback on error)
- [ ] Retry logic handles temporary connection failures
- [ ] Seed data script creates user, prompts, and sample items
- [ ] Seed script is idempotent (can run multiple times safely)
- [ ] Database contains test data after running seed script
- [ ] Documentation explains how to use connection module
- [ ] All functions have docstrings and usage examples
