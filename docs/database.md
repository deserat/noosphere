# Database Architecture

## Overview

Noosphere uses **PostgreSQL 14+** with the **pgvector** extension for relational data storage and vector similarity search.

**Key Technologies**:
- PostgreSQL 16.11 - Relational database
- pgvector 0.8.1 - Vector similarity search (1536-dimension embeddings)
- SQLAlchemy 2.0+ - Python ORM
- Alembic - Database migrations
- psycopg2 - PostgreSQL adapter

## Schema Design

### Core Tables (9 tables)

#### 1. items
Primary knowledge items with metadata and embeddings.

```sql
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    state VARCHAR(50) DEFAULT 'not-started',
    priority INTEGER DEFAULT 3,
    embedding vector(1536),  -- OpenAI/Claude embeddings
    file_path VARCHAR(1000) UNIQUE,
    content_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    next_surface TIMESTAMP,
    last_surfaced TIMESTAMP,
    surface_count INTEGER DEFAULT 0,
    user_id UUID REFERENCES users(id)
);

CREATE INDEX idx_items_embedding ON items USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_items_next_surface ON items (next_surface) WHERE state != 'completed';
CREATE INDEX idx_items_category ON items (category);
```

**Purpose**: Core knowledge item storage
**Relationships**: Many-to-one with users, many-to-many with tags
**Vector Search**: Semantic similarity for related item discovery

#### 2. item_links
Relationships and connections between items.

```sql
CREATE TABLE item_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    target_item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    link_type VARCHAR(50) DEFAULT 'related',  -- related, depends-on, inspired-by
    strength FLOAT DEFAULT 0.5,  -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_item_id, target_item_id, link_type)
);

CREATE INDEX idx_item_links_source ON item_links (source_item_id);
CREATE INDEX idx_item_links_target ON item_links (target_item_id);
```

**Purpose**: Graph of knowledge relationships
**Use Cases**: Related items, dependency tracking, inspiration chains

#### 3. conversations
AI conversation history and context.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES items(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id),
    messages JSONB NOT NULL,  -- Array of {role, content, timestamp}
    total_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_item ON conversations (item_id);
CREATE INDEX idx_conversations_user ON conversations (user_id);
```

**Purpose**: Preserve AI conversation context
**Data Format**: JSONB array of messages with roles (system, user, assistant)

#### 4. users
User accounts and preferences.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**Purpose**: User management (single-user in Phase 1, multi-user later)

#### 5. user_config
User preferences and settings.

```sql
CREATE TABLE user_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    default_surface_cadence INTEGER DEFAULT 1,  -- days
    category_cadences JSONB,  -- {category: days}
    ai_model VARCHAR(100) DEFAULT 'claude-3-5-sonnet-20241022',
    notification_time TIME DEFAULT '08:00:00',
    config JSONB,  -- Additional settings
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Purpose**: Personalization and preferences
**JSONB Examples**:
- `category_cadences`: `{"ideas": 3, "tasks": 1, "notes": 7}`
- `config`: Flexible key-value for future settings

#### 6. prompts
AI prompt templates and versions.

```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    template TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_prompts_active ON prompts (name) WHERE is_active = true;
```

**Purpose**: Versioned prompt management
**Use Cases**: Classification prompts, triage prompts, surfacing logic

#### 7. token_usage
AI API token tracking and costs.

```sql
CREATE TABLE token_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    operation VARCHAR(100) NOT NULL,  -- classify, embed, chat
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 6) DEFAULT 0.0,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_token_usage_user ON token_usage (user_id);
CREATE INDEX idx_token_usage_timestamp ON token_usage (timestamp);
```

**Purpose**: Cost tracking and usage analytics
**Aggregations**: Daily/monthly usage by operation type

#### 8. audit_log
System activity and change tracking.

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,  -- create, update, delete, sync
    entity_type VARCHAR(100) NOT NULL,  -- item, user, config
    entity_id UUID,
    changes JSONB,  -- Before/after state
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_log (user_id);
CREATE INDEX idx_audit_timestamp ON audit_log (timestamp);
CREATE INDEX idx_audit_entity ON audit_log (entity_type, entity_id);
```

**Purpose**: Security, debugging, compliance
**Changes Format**: `{"before": {...}, "after": {...}}`

#### 9. tags
Item categorization and filtering.

```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7),  -- Hex color code
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE item_tags (
    item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, tag_id)
);

CREATE INDEX idx_item_tags_item ON item_tags (item_id);
CREATE INDEX idx_item_tags_tag ON item_tags (tag_id);
```

**Purpose**: Flexible tagging system
**Relationship**: Many-to-many with items

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐
│   users     │──────<│ user_config  │
└──────┬──────┘       └──────────────┘
       │
       │ 1:N
       │
┌──────▼──────┐       ┌──────────────┐
│   items     │──────<│ item_links   │
└──────┬──────┘       └──────────────┘
       │                      ▲
       │ 1:N                  │
       │                      │
┌──────▼──────────┐           │
│ conversations   │           │
└─────────────────┘           │
                              │
┌──────────────┐       ┌──────┴───────┐
│    tags      │──────<│  item_tags   │
└──────────────┘       └──────────────┘
```

## Migration Strategy

### Alembic Workflow

**Create Migration**:
```bash
cd api-service
source .venv/bin/activate
alembic revision --autogenerate -m "Description of changes"
```

**Review Migration**: Always review autogenerated migrations in `alembic/versions/`

**Apply Migration**:
```bash
alembic upgrade head
```

**Rollback**:
```bash
alembic downgrade -1  # One step back
alembic downgrade base  # Complete rollback
```

**Check Status**:
```bash
alembic current
alembic history
```

### Best Practices

1. **Review Autogenerate**: Always check generated migrations for correctness
2. **Add Data Migrations**: Include data transformations when needed
3. **Test Rollback**: Verify downgrades work before deploying
4. **Version Control**: Commit migrations with code changes
5. **Production Safety**: Test migrations on staging first

## Connection Configuration

### Connection String Format

```
postgresql://user:password@host:port/database
```

**Development**:
```
postgresql://noosphere_user:dev_password@localhost:5432/noosphere
```

**Production** (example):
```
postgresql://noosphere_user:secure_password@db.example.com:5432/noosphere?sslmode=require
```

### Connection Pooling

SQLAlchemy engine with pooling (configured in EPIC-2-3):

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    echo=False  # Set to True for SQL logging
)
```

### SSL/TLS

**Development**: No SSL (localhost)
**Production**: Require SSL with `?sslmode=require` in connection string

## Performance Considerations

### Indexing Strategy

**Items Table**:
- Vector index: IVFFlat for approximate nearest neighbor search
- Timestamp indexes: next_surface, created_at for time-based queries
- Category index: Frequent filtering by category

**Trade-offs**:
- IVFFlat: Fast approximate search, requires periodic VACUUM ANALYZE
- GIN indexes on JSONB: Fast lookup, slower writes
- B-tree on timestamps: Efficient range queries

### Query Optimization

**Vector Search**:
```sql
-- Use LIMIT for top-k queries
SELECT * FROM items
ORDER BY embedding <-> query_embedding
LIMIT 10;

-- Add filters BEFORE distance calculation
SELECT * FROM items
WHERE category = 'ideas'
ORDER BY embedding <-> query_embedding
LIMIT 10;
```

**JSONB Queries**:
```sql
-- Index-friendly containment
SELECT * FROM user_config
WHERE category_cadences @> '{"ideas": 3}';

-- Extract values efficiently
SELECT config->>'theme' FROM user_config;
```

### Vacuum and Analyze

**Routine Maintenance**:
```sql
VACUUM ANALYZE items;  -- After bulk updates
VACUUM ANALYZE conversations;  -- After large JSONB writes
```

**Autovacuum**: Enabled by default, monitors and maintains tables automatically

## Security

### Access Control

**Principle of Least Privilege**:
- `noosphere_user`: Full access to noosphere database only
- No superuser privileges
- No access to other databases

**Grant Structure**:
```sql
GRANT ALL PRIVILEGES ON DATABASE noosphere TO noosphere_user;
GRANT ALL ON SCHEMA public TO noosphere_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO noosphere_user;
```

### SQL Injection Prevention

**Use Parameterized Queries**:
```python
# ✓ Good (SQLAlchemy ORM)
session.query(Item).filter(Item.category == user_input).all()

# ✓ Good (SQLAlchemy Core)
connection.execute(
    text("SELECT * FROM items WHERE category = :cat"),
    {"cat": user_input}
)

# ✗ Bad (vulnerable to SQL injection)
connection.execute(f"SELECT * FROM items WHERE category = '{user_input}'")
```

**ORM Benefits**:
- SQLAlchemy automatically escapes parameters
- Type validation prevents common attacks
- Reduces raw SQL surface area

### Credentials Management

**Development**:
- `.env` file (never committed)
- Simple passwords acceptable for localhost

**Production**:
- Secret manager (AWS Secrets Manager, HashiCorp Vault)
- Strong passwords (16+ characters, random)
- Rotate credentials regularly
- Audit access logs

## Backup and Recovery

### Backup Strategy

**pg_dump** (logical backup):
```bash
# Full backup
pg_dump -U noosphere_user -d noosphere > noosphere_backup.sql

# Schema only
pg_dump -U noosphere_user -d noosphere --schema-only > schema.sql

# Data only
pg_dump -U noosphere_user -d noosphere --data-only > data.sql
```

**Restore**:
```bash
psql -U noosphere_user -d noosphere < noosphere_backup.sql
```

**Backup Schedule**:
- Development: Manual as needed
- Production: Daily automated backups, 30-day retention

### Point-in-Time Recovery

**Production Only**:
- Enable WAL archiving
- Continuous archiving with pg_basebackup
- Recovery to any point in time

## Monitoring and Health Checks

### Database Health

**Connection Check**:
```python
from sqlalchemy import text

def check_database_health(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

**Metrics to Monitor**:
- Connection pool utilization
- Query execution time (slow query log)
- Table bloat (VACUUM effectiveness)
- Index usage statistics

### Slow Query Detection

**Enable Logging**:
```sql
ALTER DATABASE noosphere SET log_min_duration_statement = 1000;  -- 1 second
```

**Review Logs**:
```bash
tail -f /var/log/postgresql/postgresql-16-main.log | grep "duration:"
```

## Troubleshooting

### Common Issues

**Connection Refused**:
```bash
# Check PostgreSQL running
pg_isready -h localhost -p 5432

# Start PostgreSQL
brew services start postgresql@16  # macOS
sudo systemctl start postgresql    # Linux
```

**Permission Denied**:
```sql
-- Grant missing permissions
GRANT ALL ON SCHEMA public TO noosphere_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO noosphere_user;
```

**pgvector Extension Not Found**:
```bash
# Verify extension installed
ls $(pg_config --pkglibdir)/vector.so
ls $(pg_config --sharedir)/extension/vector*

# Rebuild if missing (see Step 1 of setup)
```

**Alembic Import Errors**:
```python
# Ensure Base is defined in app/db/base.py
# Ensure models are imported in base.py (for autogenerate)
# Check DATABASE_URL is set in .env
```

**Vector Index Not Used**:
```sql
-- Check query plan
EXPLAIN ANALYZE
SELECT * FROM items
ORDER BY embedding <-> '[...]'
LIMIT 10;

-- Ensure index exists
\d items
```

## Next Steps

**After Database Setup (This Story - EPIC-2-1)**:
- ✅ PostgreSQL running with pgvector
- ✅ Database and user created
- ✅ Alembic initialized
- ✅ Connection verified

**EPIC-2-2: Create SQLAlchemy Models**:
- Implement 9 core table models
- Add relationships and constraints
- Create initial migration
- Test CRUD operations

**EPIC-2-3: Database Connection Module**:
- Session management with context managers
- Connection pooling configuration
- Health check endpoints
- Error handling patterns

**EPIC-5-1: API Service Integration**:
- FastAPI dependency injection for sessions
- Database health check in /health endpoint
- Middleware for automatic session cleanup

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
