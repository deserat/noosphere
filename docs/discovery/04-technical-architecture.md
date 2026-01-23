# Technical Architecture

## System Overview

### Two Deployment Targets

**Server (Python):**
- API + AI + Scheduler (integrated)

**Client (Rust):**
- CLI (REPL + TUI)
- Sync Service (file watcher)

```
┌─────────────────────────────────────────────────────────┐
│ CLI (Rust - REPL/TUI) - CLIENT                         │
└────────┬────────────────────────────────────────────────┘
         │ HTTP REST + WebSocket
┌────────▼────────────────────────────────────────────────┐
│ API + AI + Scheduler Service (Python/FastAPI) - SERVER │
│  - REST endpoints (capture, triage, review)            │
│  - WebSocket endpoints (chat, work)                    │
│  - LiteLLM integration                                 │
│  - Scheduler (digest, surfacing) - integrated          │
└────────┬────────────────────────────────────────────────┘
         │ read/write (DATABASE ONLY)
         ▼
┌─────────────────────┐     ┌────────────────────────────┐
│ PostgreSQL+pgvector │     │ File Vault                 │
│  - Items            │     │  ~/noosphere-vault/        │
│  - Links            │     │  - Markdown files          │
│  - Conversations    │     │  - Category folders        │
│  - Audit log        │     │  - Frontmatter metadata    │
└─────────────────────┘     └────────┬───────────────────┘
         ▲                           │ read/write/watch
         │                           ▼
         │                  ┌────────────────────────────┐
         │                  │ Sync Service (Rust)        │
         │                  │  - File watcher (notify)   │
         │                  │  - File parser (frontmatter│
         └─────────────────│  - File writer (markdown)  │
                  HTTP      │  - File locking (fs2)      │
                            │  - HTTP client (reqwest)   │
                            └────────────────────────────┘
```

### Service Responsibilities

**1. API + AI + Scheduler Service** (Python/FastAPI + LiteLLM) - SERVER
- HTTP REST API for all operations
- WebSocket for conversational interfaces (chat, editing)
- AI operations: classification, embeddings, conversation, summarization
- All database operations (owns SQLAlchemy models)
- Scheduler background task (digest generation, surfacing calculations)
- Receives parsed item data from sync-service via REST API
- NO file system access - stateless server
- Runs on localhost only (no auth for MVP)
- Port: 8000 (configurable)

**2. Sync Service** (Rust) - LOCAL CLIENT
- File watcher (notify crate)
- Detects file changes (create, modify, delete, move)
- Reads and parses markdown files with YAML frontmatter
- Writes markdown files to vault (atomic operations)
- File locking mechanism (prevents concurrent writes)
- Computes content hashes (SHA-256) for change detection
- Syncs vault ↔ API server via HTTP
- NO database access (API owns database)
- Runs continuously in background

**3. CLI** (Rust) - CLIENT
- REPL + TUI interface
- HTTP/WebSocket client for API communication
- No business logic (all in API)
- User interaction only

### Architecture Principles
- **Clean client/server separation**: No shared code between services
- **Vault operations in Rust only**: sync-service and cli touch ~/noosphere-vault/
- **API is stateless**: Database operations only, NO filesystem access
- **Sync-service is the translator**: Vault ↔ API communication via HTTP
- **Stateless services**: Coordinate via PostgreSQL and HTTP
- **Future-ready**: Clean separation enables cloud migration

## FastAPI Endpoints

### REST API

```python
# Capture
POST   /api/capture              # Capture new item
  Body: { "text": "I need to call dentist", "source": "cli" }
  Returns: { "item_id": "uuid", "suggested_category": "...", "confidence": 0.92 }

# Triage
GET    /api/triage               # Get uncategorized items
  Returns: [{ "id": "uuid", "text": "...", "ai_suggestion": {...} }]

POST   /api/triage/approve       # Approve AI classification (bulk)
  Body: { "item_ids": ["uuid1", "uuid2"], "approvals": {...} }

POST   /api/triage/modify        # Modify classification for single item
  Body: { "item_id": "uuid", "category": "...", "subcategory": "...", "tags": [...] }

# Review
GET    /api/review               # Get items surfacing today
  Query: ?user_id=uuid
  Returns: { "due_today": [...], "resurfacing": [...] }

POST   /api/items/{id}/defer     # Defer item
  Body: { "cadence": "tomorrow" }  # or "user_cadence"

POST   /api/items/{id}/complete  # Complete/archive item
  Body: { "state": "completed" }  # or "archived"

POST   /api/items/{id}/move      # Recategorize (move file)
  Body: { "category": "...", "subcategory": "..." }

# Search & Query
GET    /api/search               # Search items (semantic + full-text)
  Query: ?q=meditation&semantic=true&limit=10
  Returns: [{ "id": "...", "title": "...", "similarity": 0.85 }]

GET    /api/items/{id}           # Get item details
  Returns: { "id": "...", "title": "...", "content": "...", ... }

# Sync (called by sync-service)
POST   /api/sync/file-changed    # Sync file change from sync-service
  Body: { "file_path": "...", "content": "...", "content_hash": "..." }
  Returns: { "status": "updated" | "conflict", "item_id": "..." }

# System
GET    /health                   # Health check
```

### WebSocket Endpoints

```python
WS     /api/chat                 # General conversation
  Client sends: { "type": "message", "content": "what's due today?" }
  Server sends: { "type": "message", "content": "You have 3 items..." }
                { "type": "mode_change", "mode": "review" }

WS     /api/work/{item_id}       # Work on item (editing mode)
  Client sends: { "type": "message", "content": "expand introduction" }
  Server sends: { "type": "thinking", "content": "..." }
                { "type": "diff", "changes": [{op: "add", line: 5, text: "..."}] }
                { "type": "message", "content": "Apply these changes?" }
  Client sends: { "type": "approve" }
  Server sends: { "type": "saved", "item_id": "..." }
```

## File System Architecture

### Source of Truth: File System
- **All changes written to files first**
- Sync service reads files → updates database
- Database is derived/cached view for fast queries
- Markdown + YAML frontmatter is canonical format

### File Operations Safety

**Lock Files (Rust - sync-service):**
```rust
// Pseudo-code for sync-service file write
use fs2::FileExt;
use std::fs::{File, rename};
use std::io::Write;

fn write_item(file_path: &Path, frontmatter: &str, content: &str) -> Result<()> {
    let lock_path = file_path.with_extension("lock");

    // Acquire lock (wait if locked)
    let lock_file = File::create(&lock_path)?;
    lock_file.lock_exclusive()?;

    // Write to temp file
    let temp_path = file_path.with_extension("tmp");
    let mut temp_file = File::create(&temp_path)?;
    write!(temp_file, "{}\n\n{}", frontmatter, content)?;
    temp_file.sync_all()?;

    // Atomic rename
    rename(temp_path, file_path)?;

    // Release lock (auto on drop)
    Ok(())
}
```

**Atomic Operations:**
- Write to `.tmp` file
- Atomic rename (POSIX guarantees atomicity)
- Lock file prevents concurrent writes (between sync-service and cli)

### Conflict Resolution

**Detection:**
```python
def detect_conflict(file_path, db_item):
    file_stat = os.stat(file_path)
    file_hash = compute_hash(file_path)

    file_modified = file_stat.st_mtime
    db_modified = db_item.modified.timestamp()

    # Conflict if both changed and hashes differ
    if file_modified > db_modified and file_hash != db_item.content_hash:
        return True
    return False
```

**Resolution Flow:**
1. Detect conflict (timestamps + hashes differ)
2. Block further edits:
   - Set `conflicted=true` flag in DB
   - Rename file to `{filename}.conflicted.md`
3. Write DB version to `{filename}.conflict-db.md`
4. Create triage item:
   ```markdown
   ---
   category: Inbox
   title: "Conflict: {original_title}"
   ---
   # Resolve Conflict: {original_title}

   The file was edited both in the app and externally.

   - Original: {filename}.conflicted.md
   - Database: {filename}.conflict-db.md

   Please resolve using a diff tool and tell me which to keep.
   ```
5. User resolves, tells agent: "accept current file" or "accept database version"
6. Agent validates, clears flags, resumes sync

### Sync Service Implementation (Rust)

```rust
use notify::{Watcher, RecursiveMode, Event};
use reqwest::Client;
use std::path::Path;
use tokio::fs;
use sha2::{Sha256, Digest};

struct SyncService {
    client: Client,
    api_url: String,
    vault_path: String,
}

impl SyncService {
    async fn handle_file_event(&self, event: Event) {
        for path in event.paths {
            // Skip directories and lock files
            if path.is_dir() || path.ends_with(".lock") {
                continue;
            }

            // Read file contents
            let content = match fs::read_to_string(&path).await {
                Ok(c) => c,
                Err(e) => {
                    eprintln!("Failed to read file: {}", e);
                    continue;
                }
            };

            // Parse frontmatter and compute content hash
            // (parsing code omitted for brevity)
            let mut hasher = Sha256::new();
            hasher.update(content.as_bytes());
            let hash = format!("{:x}", hasher.finalize());

            // Send parsed item data to API
            let response = self.client
                .post(format!("{}/api/sync/file-changed", self.api_url))
                .json(&serde_json::json!({
                    "file_path": path.strip_prefix(&self.vault_path).unwrap(),
                    "content": content,
                    "content_hash": hash,
                }))
                .send()
                .await;

            match response {
                Ok(resp) if resp.status().is_success() => {
                    println!("Synced: {:?}", path);
                }
                Ok(resp) => {
                    eprintln!("Sync failed: {}", resp.status());
                }
                Err(e) => {
                    eprintln!("HTTP error: {}", e);
                    // Retry logic here
                }
            }
        }
    }
}
```

## AI Integration (LiteLLM)

### Configuration

```python
# Prompts stored in database
def get_active_prompt(name: str):
    return db.query(Prompt).filter_by(name=name, active=True).first()

# Model selection by task
MODEL_CONFIG = {
    "classification": "gemini-1.5-flash",     # Fast, cheap
    "embedding": "text-embedding-3-small",    # Cost-effective
    "conversation": "gemini-1.5-pro",         # Quality for editing
    "summarization": "gemini-1.5-flash",      # Fast, good enough
}

def get_model_for_task(task: str) -> str:
    return config.get("ai", "models", task) or MODEL_CONFIG[task]
```

### Usage Patterns

**1. Classification:**
```python
async def classify_item(text: str) -> ClassificationResult:
    prompt = get_active_prompt("classification")

    response = await litellm.acompletion(
        model=get_model_for_task("classification"),
        messages=[
            {"role": "system", "content": prompt.content},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)

    # Log token usage
    log_token_usage(
        operation="classification",
        model=response.model,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        cost_usd=calculate_cost(response)
    )

    return ClassificationResult(**result)
```

**2. Embeddings:**
```python
async def generate_embedding(text: str) -> list[float]:
    response = await litellm.aembedding(
        model=get_model_for_task("embedding"),
        input=text
    )

    log_token_usage(
        operation="embedding",
        model=response.model,
        input_tokens=len(text.split()),  # Approximate
        output_tokens=0,
        cost_usd=calculate_cost(response)
    )

    return response.data[0].embedding
```

**3. Streaming Conversation:**
```python
async def stream_conversation(messages: list, websocket):
    async for chunk in await litellm.acompletion(
        model=get_model_for_task("conversation"),
        messages=messages,
        stream=True,
        temperature=0.7
    ):
        delta = chunk.choices[0].delta
        if delta.content:
            await websocket.send_json({
                "type": "content",
                "content": delta.content
            })

    # Log after completion
    log_token_usage(...)
```

### Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_llm_with_retry(model, messages, **kwargs):
    try:
        return await litellm.acompletion(model=model, messages=messages, **kwargs)
    except litellm.RateLimitError as e:
        sentry_sdk.capture_exception(e)
        raise  # Will retry
    except litellm.APIError as e:
        sentry_sdk.capture_exception(e)
        if e.status_code >= 500:
            raise  # Will retry
        else:
            return error_response(e)  # Don't retry client errors
```

## Project Structure

```
noosphere/
  cli/                      # Rust CLI (REPL + TUI) - CLIENT
    src/
      main.rs               # Entry point
      repl.rs               # REPL loop
      tui/                  # TUI components
        triage.rs
        review.rs
        editor.rs
      api_client.rs         # HTTP + WebSocket client
      config.rs
    Cargo.toml
    tests/

  sync-service/             # Rust: File watcher - LOCAL CLIENT
    src/
      main.rs               # Entry point
      watcher.rs            # File watcher (notify)
      client.rs             # HTTP client for API
      vault/                # Vault filesystem operations
        parser.rs           # Markdown + frontmatter parser
        writer.rs           # Markdown file writer
        lock.rs             # File locking (fs2)
        template.rs         # Markdown templates
        hash.rs             # Content hashing (SHA-256)
      config.rs             # Config loader
    Cargo.toml
    tests/

  api-service/              # Python: API + AI + Scheduler - SERVER
    src/
      main.py               # FastAPI app entry (includes scheduler)
      api/
        capture.py          # Capture endpoints
        triage.py           # Triage endpoints
        review.py           # Review endpoints
        sync.py             # Sync endpoint
        chat.py             # WebSocket chat
        work.py             # WebSocket editing
      ai/
        litellm_client.py   # LiteLLM wrapper
        classification.py   # Classification logic
        embeddings.py       # Embedding generation
        conversation.py     # Conversational agent
      scheduler/            # Integrated scheduler
        digest.py           # Digest generation
        surfacing.py        # Calculate next_surface dates
        tasks.py            # Periodic tasks
      models/               # SQLAlchemy models
        __init__.py
        item.py
        link.py
        conversation.py
        user.py
        prompt.py
        token_usage.py
        audit.py
      config/
        __init__.py
        loader.py           # Config file + env var loading
        database.py         # Database connection
    migrations/             # Alembic migrations
      versions/
      env.py
      alembic.ini
    tests/
    requirements.txt
    pyproject.toml

  docs/
    discovery/              # Discovery documentation
    agents/                 # Agent context files
      README.md
      architecture.md
      standards.md
    project/                # Project documentation
      implementation-roadmap.md

  scripts/
    start_api.sh            # Start API service
    start_sync.sh           # Start sync service
    setup_db.sh             # Database initialization

  AGENTS.md                 # Top-level agent overview
  .gitignore
  README.md
```

**Key architecture decisions:**
- **No shared/ directory**: Clean client/server separation
- **Scheduler integrated**: Part of api-service, not separate
- **Vault operations in Rust only**: sync-service owns file parsing/writing
- **API is stateless**: Database and AI operations only, NO filesystem access
- **Each service has own tests**: No cross-service dependencies

## Configuration Management

### Config Files

```yaml
# config/default.yaml
database:
  host: localhost
  port: 5432
  name: noosphere
  user: noosphere
  password: ${DATABASE_PASSWORD}  # From env var

vault:
  path: ~/noosphere-vault

api:
  host: localhost
  port: 8000
  cors_origins: ["http://localhost:*"]

scheduler:
  digest_time: "07:00"
  surfacing_interval: 300  # 5 minutes

ai:
  default_provider: anthropic
  models:
    classification: gemini-1.5-flash
    embedding: text-embedding-3-small
    conversation: gemini-1.5-pro
    summarization: gemini-1.5-flash
  classification_threshold: 0.6

sentry:
  dsn: ${SENTRY_DSN}
  environment: development
  traces_sample_rate: 0.1

logging:
  level: INFO
  format: json
```

### Environment Variables

```bash
# Override specific config values
export NOOSPHERE_DATABASE__PASSWORD=secret
export NOOSPHERE_VAULT__PATH=/custom/path
export NOOSPHERE_AI__MODELS__CONVERSATION=claude-3-5-sonnet
export NOOSPHERE_SENTRY__DSN=https://...
export NOOSPHERE_LOGGING__LEVEL=DEBUG
```

### Config Loading (Python)

```python
import yaml
import os
from typing import Any

class Config:
    def __init__(self, config_file: str = "config/default.yaml"):
        with open(config_file) as f:
            self._config = yaml.safe_load(f)
        self._load_env_overrides()

    def _load_env_overrides(self):
        for key, value in os.environ.items():
            if key.startswith("NOOSPHERE_"):
                # NOOSPHERE_DATABASE__HOST -> database.host
                path = key[11:].lower().split("__")
                self._set_nested(path, value)

    def get(self, *path) -> Any:
        obj = self._config
        for key in path:
            obj = obj[key]
        return obj
```

## Technology Stack

### Core Technologies
- **Database**: PostgreSQL 14+ with pgvector extension
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **API Framework**: FastAPI (Python 3.11+)
- **WebSocket**: FastAPI WebSocket support
- **File Watching**: notify (Rust crate)
- **AI**: LiteLLM (provider-agnostic)
- **Client**: Rust 1.70+ with tokio, reqwest, ratatui/crossterm
- **Error Tracking**: Sentry
- **Testing**: pytest (Python), cargo test (Rust)

### Python Dependencies
```
# api-service/requirements.txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
pgvector>=0.2.0
litellm>=1.0.0
pydantic>=2.0.0
python-multipart>=0.0.6
watchdog>=3.0.0          # For lock file cleanup
pyyaml>=6.0
sentry-sdk[fastapi]>=1.38.0
tenacity>=8.2.0
```

### Rust Dependencies
```toml
# cli/Cargo.toml
[dependencies]
tokio = { version = "1.35", features = ["full"] }
ratatui = "0.25"
crossterm = "0.27"
reqwest = { version = "0.11", features = ["json"] }
tokio-tungstenite = "0.21"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
clap = { version = "4.4", features = ["derive"] }

# sync-service/Cargo.toml
[dependencies]
tokio = { version = "1.35", features = ["full"] }
notify = "6.1"
reqwest = { version = "0.11", features = ["json"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
serde_yaml = "0.9"
sha2 = "0.10"
```

## Development & Deployment

### Local Development Setup
```bash
# 1. Install PostgreSQL + pgvector
brew install postgresql@14 pgvector  # macOS
# or
sudo apt install postgresql-14 postgresql-14-pgvector  # Ubuntu

# 2. Create database
createdb noosphere
psql noosphere -c "CREATE EXTENSION vector;"

# 3. Python services
cd api-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py

# 4. Rust CLI
cd cli
cargo build --release
./target/release/noosphere

# 5. Run migrations
cd migrations
alembic upgrade head
```

### Running Services
```bash
# Terminal 1: API service (includes integrated scheduler)
cd api-service
uvicorn src.main:app --reload --port 8000

# Terminal 2: Sync service (Rust)
cd sync-service
cargo run

# Terminal 3: CLI
cd cli
cargo run
```

### Testing
```bash
# Python tests (api-service)
cd api-service
pytest tests/unit -v
pytest tests/integration -v

# Rust tests (CLI)
cd cli
cargo test

# Rust tests (sync-service)
cd sync-service
cargo test
```

## Future: Cloud Migration Path

**When ready to move to GCP:**
1. **API Service (with integrated scheduler)** → Cloud Run service
2. **Database** → Cloud SQL (PostgreSQL + pgvector)
3. **File Vault** → Cloud Storage + user devices (sync via client)
4. **Message Queue** → Pub/Sub (replace polling for real-time updates)
5. **Authentication** → Firebase Auth or Cloud Identity
6. **Client Services (CLI + sync-service)** → Remain local, connect to cloud API

**Architecture remains the same**, just swap:
- Local PostgreSQL → Cloud SQL
- Local files → Cloud Storage (with client-side caching)
- Scheduler polling → Cloud Scheduler triggers + Pub/Sub
- Localhost → HTTPS with auth
- Sync-service stays local, calls cloud API endpoints
