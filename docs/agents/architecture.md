# System Architecture

This document contains system-wide architectural decisions for the Noosphere project. These decisions affect multiple services and should be consulted when making cross-cutting design choices.

## Architectural Principles

### 1. Clean Client/Server Separation

**Decision**: Separate client (Rust) and server (Python) with no shared code.

**Rationale**:
- **Independent Deployment**: Services can be updated separately
- **Language Optimization**: Python for AI/data, Rust for performance/CLI
- **Clear Boundaries**: REST API defines contract
- **Parallel Development**: Teams can work independently

**Consequences**:
- **Positive**: Clear service boundaries, optimal language choice per domain
- **Negative**: Duplication of data models (Python models vs Rust structs)
- **Mitigation**: Use OpenAPI spec to generate client types from server

### 2. Local-First Architecture

**Decision**: File vault lives on user's machine, database is supplementary.

**Rationale**:
- **User Ownership**: Users own their data in portable markdown format
- **Tool Agnostic**: Works with Obsidian, VS Code, any markdown editor
- **Privacy**: Sensitive data stays local
- **Resilience**: System works offline, syncs when online

**Consequences**:
- **Positive**: User control, data portability, external tool compatibility
- **Negative**: Sync complexity, potential conflicts
- **Mitigation**: File locking, conflict detection, last-write-wins strategy

### 3. Event-Driven Sync

**Decision**: Rust sync service watches vault, triggers API updates on changes.

**Rationale**:
- **Real-Time**: Changes reflected immediately
- **Efficient**: Only sync what changed (file watching)
- **Bi-directional**: Vault → DB and DB → Vault
- **Decoupled**: Sync service is independent of API

**Consequences**:
- **Positive**: Real-time sync, resource efficient, clean separation
- **Negative**: Additional service to manage, event ordering complexity
- **Mitigation**: Event debouncing, idempotent operations

## Technology Decisions

### Backend: Python + FastAPI

**Decision**: Use Python 3.11+ with FastAPI for backend API service.

**Why Python**:
- **AI Ecosystem**: Best-in-class libraries (litellm, langchain, sentence-transformers)
- **Rapid Development**: Fast iteration for AI experimentation
- **Community**: Large ecosystem for data processing

**Why FastAPI**:
- **Performance**: Async support, competitive with Node.js
- **Type Safety**: Pydantic models provide runtime validation
- **Auto-Documentation**: OpenAPI/Swagger generation
- **Standards**: Follows RESTful conventions

**Alternatives Considered**:
- **Flask**: Too minimal, lacks async support
- **Django**: Too heavyweight, overkill for API-only service
- **Node.js**: Weaker AI ecosystem

### Client: Rust

**Decision**: Use Rust 1.70+ for CLI and sync service.

**Why Rust**:
- **Performance**: Fast startup, low resource usage for always-running sync
- **Reliability**: Memory safety, no garbage collection pauses
- **Distribution**: Single binary, easy installation
- **TUI Libraries**: Excellent ratatui for terminal interfaces

**Why ratatui + Elm Architecture**:
- **Predictable State**: Elm Architecture pattern for UI
- **Composability**: Reusable components
- **Testing**: Pure functions easy to test
- **Performance**: Fast rendering, responsive UI

**Alternatives Considered**:
- **Python**: Slower startup, distribution complexity
- **Go**: Good choice, but weaker TUI ecosystem
- **Node.js**: Heavy runtime for simple CLI

### Database: PostgreSQL + pgvector

**Decision**: Use PostgreSQL 14+ with pgvector extension.

**Why PostgreSQL**:
- **Reliability**: Battle-tested, ACID compliance
- **Features**: Rich query capabilities, JSON support
- **Vector Search**: pgvector for semantic search
- **Ecosystem**: Excellent Python (asyncpg) and migration tools (Alembic)

**Why pgvector**:
- **Native Integration**: No separate vector database needed
- **Performance**: Good enough for personal knowledge management scale
- **Simplicity**: Single database for relational + vector data
- **Cost**: Free, open source

**Alternatives Considered**:
- **SQLite**: No pgvector support, limited concurrency
- **MongoDB**: Weaker vector search, schemaless complexity
- **Pinecone/Weaviate**: Overkill for personal scale, cost

## Communication Patterns

### API: REST over HTTP

**Decision**: Use REST API with JSON for client-server communication.

**Endpoints**:
```
POST   /api/items              # Create item
GET    /api/items              # List items
GET    /api/items/{id}         # Get item
PUT    /api/items/{id}         # Update item
DELETE /api/items/{id}         # Delete item
GET    /api/items/search       # Semantic search
GET    /api/items/surface      # Get items to surface
GET    /api/health             # Health check
```

**Why REST**:
- **Simplicity**: Well-understood, easy to test
- **Tooling**: curl, Postman, browser dev tools
- **Stateless**: Each request is independent
- **Standards**: HTTP status codes, content negotiation

**Alternatives Considered**:
- **GraphQL**: Overkill for simple CRUD API
- **gRPC**: Too complex for this use case
- **WebSockets**: Not needed for current features

### File Vault: Markdown + YAML Frontmatter

**Decision**: Use markdown files with YAML frontmatter for knowledge storage.

**Format**:
```markdown
---
id: uuid-here
title: Item title
category: ideas
tags: [tag1, tag2]
created: 2024-01-15T10:00:00Z
surfaced: 2024-01-15T10:00:00Z
next_surface: 2024-01-16T10:00:00Z
cadence: daily
---

# Item Title

Item content in markdown format.
```

**Why Markdown + YAML**:
- **Human-Readable**: Easy to read and edit
- **Tool Compatible**: Works with Obsidian, VS Code, editors
- **Portable**: Plain text, no lock-in
- **Extensible**: YAML frontmatter for metadata

**Alternatives Considered**:
- **JSON**: Less human-readable
- **TOML**: Less common, fewer tools
- **Database-only**: No external tool compatibility

## Data Flow Architecture

### Capture Flow

```
User Input (CLI)
    ↓
CLI captures text + metadata
    ↓
Write markdown file to vault
    ↓
Sync service detects file change (notify)
    ↓
POST /api/items (sync → API)
    ↓
API classifies with AI (litellm)
    ↓
Save to PostgreSQL with embeddings
    ↓
Return classification to sync service
    ↓
Update markdown frontmatter with classification
```

### Surfacing Flow

```
Background Scheduler (APScheduler)
    ↓
Query items where next_surface <= now
    ↓
For each item:
  - Load context (related items, recent activity)
  - Generate surfacing prompt with AI
  - Update next_surface based on cadence
    ↓
POST /api/items/{id}/surface
    ↓
CLI polls /api/items/surface
    ↓
Display surfaced items in TUI
    ↓
User interaction → Update surfacing metadata
```

### Sync Flow (Bi-directional)

```
Vault → Database:
  File changed → Sync service → API → Database

Database → Vault:
  API update → Sync service → Update markdown file

Conflict Resolution:
  - Last-write-wins based on modified timestamp
  - Lock files prevent concurrent writes
```

## Security Architecture

### Authentication (Phase 2+)

**Decision**: JWT-based authentication with refresh tokens.

**Why JWT**:
- **Stateless**: No server-side session storage
- **Portable**: Works across multiple devices
- **Standard**: Well-understood, good libraries

**Implementation**:
- Access token: Short-lived (15 min), for API requests
- Refresh token: Long-lived (30 days), for token renewal
- Storage: CLI stores in OS keyring (secure)

### Data Security

**Decisions**:
- **At Rest**: File vault unencrypted (user's machine security)
- **In Transit**: HTTPS for API communication (production)
- **Database**: PostgreSQL connection encrypted (SSL)
- **Secrets**: Environment variables, never committed

## Scalability Considerations

### Current Scope (Personal Use)

**Assumptions**:
- Single user per instance
- Thousands of items, not millions
- Local deployment (user's machine)

**Design Choices**:
- **Simple Scheduler**: APScheduler (in-process)
- **Single Database**: PostgreSQL handles everything
- **No Caching**: Database is fast enough at this scale

### Future Scalability (Multi-User)

**If Scaling to Multi-User**:
- **Scheduler**: Migrate to Celery (distributed task queue)
- **Caching**: Add Redis for session storage
- **Database**: Read replicas for scalability
- **File Storage**: Move vault to S3 or similar

**When to Scale**:
- Only if multi-user version is needed
- Current architecture is optimal for personal use

## Testing Strategy

### Backend Testing

**Unit Tests** (pytest):
- CRUD operations
- AI classification logic
- Markdown parsing/writing
- Scheduler jobs

**Integration Tests**:
- API endpoints (TestClient)
- Database transactions
- File vault operations

**Test Database**:
- Separate test database (noosphere_test)
- Alembic migrations applied before tests
- Cleanup after each test

### CLI Testing

**Unit Tests** (cargo test):
- State management (App struct)
- Event handlers (handler.rs)
- UI rendering logic (ui.rs)

**Integration Tests**:
- API client communication
- File operations
- End-to-end workflows

### Sync Service Testing

**Unit Tests**:
- File watching logic
- Sync algorithms
- Conflict resolution

**Integration Tests**:
- API communication
- File vault operations
- End-to-end sync scenarios

## Deployment Architecture

### Phase 1: Local Deployment

**Components**:
- API Service: Run with uvicorn (development) or gunicorn (production)
- Sync Service: systemd service (Linux) or launchd (macOS)
- CLI: Run manually or via launcher
- Database: Local PostgreSQL or Docker container

**Startup**:
```bash
# API Service
cd api-service
source venv/bin/activate
python -m app.main

# Sync Service (background)
cd sync-service
cargo run --release &

# CLI (on demand)
cd cli
cargo run --release
```

### Phase 4: Distribution

**Installers**:
- **Linux**: .deb package (systemd services)
- **macOS**: Homebrew formula (launchd services)
- **Windows**: Installer with Windows services

**Dependencies**:
- PostgreSQL: Docker container or system installation
- Python: Bundled with PyInstaller or system Python
- Rust: Single binary, no dependencies

## Monitoring and Observability

### Health Checks

**API Health**:
- `/api/health`: Overall service health
- `/api/health/ready`: Readiness probe
- `/api/health/live`: Liveness probe

**Monitoring Points**:
- Database connection status
- Scheduler running state
- API response times
- Background job execution

### Logging

**Structured Logging**:
```python
# Python (app.main)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)
```

```rust
// Rust (CLI/Sync)
tracing::info!(
    target = "noosphere::sync",
    file = ?path,
    "File change detected"
);
```

**Log Levels**:
- ERROR: Critical failures requiring attention
- WARN: Potential issues, degraded functionality
- INFO: Normal operations, important events
- DEBUG: Detailed debugging information

## Error Handling

### API Errors

**HTTP Status Codes**:
- 200: Success
- 201: Created
- 400: Bad Request (client error)
- 404: Not Found
- 500: Internal Server Error

**Error Response Format**:
```json
{
  "error": "ItemNotFound",
  "message": "Item with ID abc123 not found",
  "details": {}
}
```

### CLI Errors

**User-Friendly Messages**:
- Network errors: "Cannot connect to API service. Is it running?"
- File errors: "Cannot write to vault. Check permissions."
- Validation errors: "Title is required."

### Sync Service Errors

**Resilience**:
- Retry with exponential backoff
- Log errors but don't crash
- Alert user if persistent failures

## Configuration Management

### Environment Variables

**Standard Variables**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/noosphere
DB_POOL_SIZE=5

# Vault
VAULT_PATH=~/noosphere-vault

# AI
GEMINI_API_KEY=your-key
OPENAI_API_KEY=your-key

# API
API_HOST=127.0.0.1
API_PORT=8000
```

### Configuration Files

**API Service**: `api-service/config.yaml`
**Sync Service**: `sync-service/config.yaml`

**Precedence**: ENV vars > config.yaml > defaults

## Migration Strategy

### Database Migrations

**Alembic**:
- All schema changes via migrations
- Never manual SQL changes
- Migration files committed to git
- Reversible when possible

**Process**:
```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Data Migrations

**Backfill Scripts**:
- Separate from schema migrations
- Idempotent (safe to rerun)
- Documented in migration file
- Tested before production

## Architectural Decision Records (ADR)

All major architectural decisions follow ADR format:

**Template**:
```markdown
## ADR-XXX: [Title]

**Date**: YYYY-MM-DD
**Status**: Accepted | Proposed | Deprecated
**Deciders**: [Names/Roles]

### Context
[Situation and problem statement]

### Decision
[Chosen solution]

### Consequences
- Positive: [Benefits]
- Negative: [Trade-offs]

### Alternatives Considered
- [Alternative 1]: [Why not chosen]
- [Alternative 2]: [Why not chosen]
```

## Evolution and Updates

This architecture document evolves with the project:

- **Phase 1**: Foundation (current architecture)
- **Phase 2**: AI Classification (add classification details)
- **Phase 3**: Surfacing (add surfacing architecture)
- **Phase 4**: Distribution (add deployment details)

Update this document when:
- Making system-wide architectural changes
- Adding new services or components
- Changing inter-service communication
- Modifying data flow patterns

## References

- [Implementation Roadmap](../project/implementation-roadmap.md)
- [User Stories](../project/stories/README.md)
- [Python Standards](standards.md#python-standards)
- [Rust Standards](standards.md#rust-standards)
