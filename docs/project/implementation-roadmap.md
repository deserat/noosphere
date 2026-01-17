# Noosphere - Implementation Roadmap

**Target:** Local-first, fully functional second brain system

---

## Phase 1: Foundation

**Deliverable:** Empty vault, working database, basic project structure, runnable (but minimal) services

### 1.1 Project Setup & Repository Structure
- Create root noosphere/ directory structure
- Create subdirectories: cli/, api-service/, sync-service/, docs/
- Create api-service subdirectories: src/api/, src/ai/, src/models/, src/scheduler/, src/vault/, src/config/, migrations/, tests/
- Create sync-service subdirectories: src/, tests/
- Create cli subdirectories: src/, tests/
- Initialize git repository in root
- Create comprehensive .gitignore (Python __pycache__, Rust target/, .env, venv/, .vscode/, .idea/, etc.)
- Create top-level README.md with project overview
- Create docs/setup.md with development environment setup instructions
- Create docs/agents/ directory
- Create docs/agents/README.md (multi-agent workflow overview)
- Create docs/agents/architecture.md (system-wide architecture decisions)
- Create docs/agents/standards.md (Python and Rust coding standards)
- Create AGENTS.md in api-service/ (API service agent context and boundaries)
- Create AGENTS.md in sync-service/ (sync service agent context and boundaries)
- Create AGENTS.md in cli/ (CLI agent context and boundaries)

### 1.2 Python Environment Setup
- Create Python virtual environment for api-service/
- Create requirements.txt for api-service:
  - FastAPI, uvicorn, SQLAlchemy, alembic, psycopg2-binary, pgvector, litellm, python-dotenv, pydantic, pyyaml, watchdog (for lock cleanup)
- Install dependencies in venv

### 1.3 Rust Client Setup
- Initialize Cargo project in cli/ directory
- Add initial dependencies to cli/Cargo.toml: tokio, reqwest, serde, serde_json, clap, crossterm, ratatui
- Create basic cli/src/main.rs with minimal CLI structure
- Initialize Cargo project in sync-service/ directory
- Add initial dependencies to sync-service/Cargo.toml: tokio, reqwest, serde, serde_json, notify, serde_yaml
- Create basic sync-service/src/main.rs with minimal service structure
- Verify Rust toolchain and compilation works for both projects

### 1.4 Database Installation & Configuration
- Install PostgreSQL 14+ locally
- Install pgvector extension for PostgreSQL
- Create local database: `noosphere`
- Create database user with appropriate permissions
- Document connection string format in .env.example

### 1.5 SQLAlchemy Models - Core Tables
- Create api-service/src/models/__init__.py
- Create api-service/src/models/base.py with declarative base
- Create api-service/src/models/user.py (users table)
- Create api-service/src/models/user_config.py (user_config table)
- Create api-service/src/models/item.py (items table with pgvector column)
- Create api-service/src/models/item_link.py (item_links table)
- Create api-service/src/models/conversation.py (conversations table)
- Create api-service/src/models/prompt.py (prompts table)
- Create api-service/src/models/token_usage.py (token_usage table)
- Create api-service/src/models/audit_log.py (audit_log table)

### 1.6 Database Migrations
- Set up Alembic in api-service/migrations/ directory
- Configure alembic.ini with database connection
- Create env.py to load models from api-service/src/models/
- Generate initial migration from models
- Apply migration to create all tables
- Verify tables and indexes created correctly

### 1.7 Database Connection Module
- Create api-service/src/config/database.py with connection pooling
- Create session management utilities
- Implement health check function
- Add connection retry logic with exponential backoff
- Document usage patterns

### 1.8 File Vault Structure
- Create ~/noosphere-vault/ directory
- Create category folders: Inbox/, People/, Projects/, Ideas/, Admin/
- Create .noosphere-metadata file with vault configuration
- Document vault structure in docs/vault-structure.md

### 1.9 Markdown File Template & Utilities (API Service Only)
- Create api-service/src/vault/template.py with frontmatter template
- Create api-service/src/vault/parser.py for parsing markdown + frontmatter
- Create api-service/src/vault/writer.py for writing markdown with frontmatter
- Implement content_hash computation (SHA-256)
- Create unit tests in api-service/tests/

### 1.10 Lock File Implementation (API Service Only)
- Create api-service/src/vault/lock.py with lock file context manager
- Implement acquire lock (create .lock file)
- Implement release lock (remove .lock file)
- Add timeout handling for stale locks
- Add lock cleanup on process termination
- Create unit tests in api-service/tests/

### 1.11 Configuration System
- Create api-service/config/default.yaml with sections:
  - database (host, port, name, user)
  - vault (path)
  - scheduler (digest_time, poll_interval)
  - ai (providers, models for classification/embedding/conversation)
  - logging (level, format)
- Create sync-service/config/default.yaml with sections:
  - api (host, port)
  - vault (path)
  - sync (watch_delay, poll_interval)
  - logging (level, format)
- Create config/local.yaml.example templates for both
- Document all configuration options in docs/configuration.md

### 1.12 Configuration Loaders
- Create api-service/src/config/loader.py
  - YAML file loading with override precedence
  - Environment variable parsing (NOOSPHERE_DATABASE__HOST format)
  - Validation and access helpers
  - Unit tests in api-service/tests/
- Create sync-service/src/config.rs (Rust config module)
  - YAML loading with serde_yaml
  - Environment variable support
  - API endpoint and vault path configuration
  - Unit tests in sync-service/tests/

### 1.13 Seed Data Script
- Create api-service/migrations/seed_data.py
- Create seed user (single user for MVP)
- Create sample prompts (classification prompt v1)
- Create sample items in each category for testing
- Generate embeddings placeholders (zeros for now)
- Document how to run seed script

### 1.14 Basic Service Scaffolding
- Create api-service/src/main.py with minimal FastAPI app
  - Health check endpoint
  - Database connection verification
  - Scheduler background task (minimal polling loop)
- Create sync-service/src/main.rs with minimal Rust service
  - File watcher setup (notify crate)
  - HTTP client for API calls (reqwest)
  - Basic file change detection
- Verify api-service can connect to database
- Verify sync-service can compile and run
- Create start scripts (scripts/start_api.sh, scripts/start_sync.sh)

### 1.15 Development Tooling
- Create pytest.ini for test configuration
- Create .flake8 or ruff.toml for linting
- Create pyproject.toml for formatting (black)
- Add pre-commit hook configuration (optional for MVP)
- Document development workflow in docs/development.md

**Phase 1 Exit Criteria:**
- API service starts without errors (with integrated scheduler)
- Sync service starts without errors
- Database tables exist and are queryable (9 tables total)
- Vault directory structure created (5 category folders)
- API service can parse and write markdown files with frontmatter
- Lock files prevent concurrent file access
- Configuration loads from YAML and env vars in both services
- Seed data populates test items (in DB and as files)
- Health check endpoint returns success
- Sync service can detect file changes (even if not processing yet)
- No shared code between services

---

## Phase 2: Core Capture & Classification

**Deliverable:** Can capture items via CLI, AI classifies them, saved as markdown files, synced to database

### 2.1 API Service - Capture Endpoint
- FastAPI app setup
- POST /api/capture endpoint
- Parse frontmatter and content
- Write to file system with lock
- Basic item creation in DB
- Return item ID and classification

### 2.2 API Service - Sync Endpoint
- POST /api/sync/file-changed endpoint
- Accept raw file contents from sync-service
- Parse frontmatter and content
- Update item in DB
- Compute and verify content_hash
- Basic conflict detection (timestamp comparison)

### 2.3 AI Integration - Classification
- LiteLLM setup and configuration
- Classification prompt (store in DB)
- Category/subcategory/tag extraction
- Confidence scoring
- Structured JSON output parsing
- Token usage logging
- Error handling and retries
- Unit tests for classification

### 2.4 Sync Service - File Watching (Rust)
- notify crate integration for file watching
- Detect file changes (create, modify, delete, move)
- Read raw file contents
- Compute content_hash (SHA-256)
- Call POST /api/sync/file-changed with raw contents (reqwest)
- Error handling and retry logic
- Unit tests for file watching and HTTP client

### 2.5 CLI - Basic Capture
- Simple REPL
- HTTP client for /api/capture
- Display confirmation
- Display AI classification results
- Error display

**Phase 2 Exit Criteria:**
- Can capture items via CLI
- AI correctly classifies items
- Items saved as markdown files
- Files synced to database
- Classification confidence displayed

---

## Phase 3: Triage Mode

**Deliverable:** Interactive triage mode, can categorize multiple items quickly

### 3.1 API Endpoints
- GET /api/triage - retrieve uncategorized items
- POST /api/triage/approve - bulk approve classifications
- POST /api/triage/modify - modify single item classification
- Response formatting with AI suggestions

### 3.2 CLI - TUI Triage Panel
- ratatui/cursive setup
- Checkbox list component
- Display AI suggestions with confidence
- Navigation (up/down, space to toggle, enter to proceed)
- Bulk approval action
- Conversational fallback for modifications
- Mode transition (TUI → REPL for conversation)

### 3.3 File Operations
- Move file from Inbox to category folder
- Update frontmatter metadata (category, subcategory, tags, state)
- Create subcategory folders on-demand
- Handle filename conflicts (append number)
- Update database after move

**Phase 3 Exit Criteria:**
- TUI triage panel displays uncategorized items
- Can bulk approve AI suggestions
- Can modify classifications conversationally
- Items move to correct category folders
- Frontmatter updated correctly

---

## Phase 4: Review & Surfacing

**Deliverable:** Morning digest, review workflow, items resurface based on cadence

### 4.1 Surfacing Logic
- Calculate `next_surface` dates
- Implement cascading cadence rules:
  - Base (next day)
  - General user preference
  - Category-specific rules
  - Item-specific overrides
- Surfacing query (items due/resurfacing today)
- Update `next_surface` after defer/complete actions

### 4.2 Scheduler Service
- Simple polling loop (60-second interval)
- Morning digest generation:
  - Query surfacing items
  - Format digest message
  - Write to notifications table (or trigger CLI notification)
- Surfacing date updates (periodic scan)

### 4.3 API Endpoints
- GET /api/review - get items for review
- POST /api/items/{id}/defer - defer item
- POST /api/items/{id}/complete - complete/archive item
- State transitions (not-started → in-progress → completed)

### 4.4 CLI - TUI Review Panel
- Review mode TUI layout (due today + resurfacing)
- Item list with states and summaries
- Navigation and selection
- Actions: defer, complete, work on
- Batch operations (defer all checked)
- Transition to editing mode

**Phase 4 Exit Criteria:**
- Morning digest generates at configured time
- Review panel shows items due today
- Items resurface per cadence rules
- Can defer, complete, or work on items
- State transitions work correctly

---

## Phase 5: Work/Editing Mode

**Deliverable:** Conversational editing works, changes reflected in files immediately

### 5.1 WebSocket Setup
- WS /api/work/{item_id} endpoint
- WebSocket message protocol
- Streaming conversation support
- Connection management (reconnect, timeout)

### 5.2 Conversation Engine
- LiteLLM streaming integration
- Conversation context management
- Load previous conversation history from DB
- Summarization for old conversations (RRD-style)
- Save conversation on exit
- Clarifying question detection

### 5.3 CLI - Split-Panel TUI
- Split-panel layout (left: chat, right: document)
- Markdown rendering in right panel
- Diff highlighting (additions, deletions)
- Approval flow (y/n prompt)
- Real-time updates
- Auto-detect completion ("done" keyword or agent prompt)

### 5.4 File Editing
- Apply changes to markdown content
- Lock file acquisition
- Immediate save on approval
- Update frontmatter (last_worked, state)
- Trigger sync to database
- Return to review mode (if came from there)

**Phase 5 Exit Criteria:**
- WebSocket connection works
- Can edit items conversationally
- Changes shown in diff panel
- Changes saved immediately on approval
- Conversation history preserved
- Returns to review mode correctly

---

## Phase 6: Semantic Features

**Deliverable:** Semantic search works, Related sections auto-generated, tag suggestions appear

### 6.1 Embeddings
- Embedding generation function (via LiteLLM)
- Async job queue for embedding updates
- Generate on item create/modify
- Store in pgvector column
- Update `embedding_updated` timestamp

### 6.2 Semantic Search
- Vector similarity queries (pgvector)
- GET /api/search endpoint
- Combined semantic + full-text search
- Relevance scoring
- CLI search command

### 6.3 Related Section Generation
- Detect semantically similar items
- Generate "why related" explanations
- Update markdown Related section
- Store in `item_links` table (link_type='semantic')
- Periodic regeneration task

### 6.4 Tag Suggestions
- Analyze existing tags via embeddings
- Suggest tags when creating items
- Tag promotion monitoring:
  - Detect frequently used tags
  - Identify semantic clusters
  - Suggest subcategory creation
- User approval flow for promotions

**Phase 6 Exit Criteria:**
- Embeddings generated for all items
- Semantic search returns relevant results
- Related sections appear in markdown files
- Tag suggestions shown during capture
- Tag promotion suggestions work

---

## Phase 7: Polish & Testing

**Deliverable:** Stable, tested, documented MVP

### 7.1 Error Handling
- Sentry integration (all services)
- Graceful degradation:
  - AI unavailable → manual categorization
  - Database down → read-only file mode
  - Sync failures → retry with backoff
- User-friendly error messages
- Validation for user inputs
- Confirmation prompts for destructive actions

### 7.2 Testing
- Unit tests for core functions:
  - Classification logic
  - File operations
  - Sync logic
  - Surfacing calculations
- Integration tests for workflows:
  - Capture → triage → categorize
  - Review → defer/complete
  - Editing flow
- End-to-end CLI testing
- Coverage reporting

### 7.3 Documentation
- Setup guide (README.md)
- User manual (how to use each mode)
- API documentation (OpenAPI/Swagger)
- Configuration reference
- Troubleshooting guide
- Contributing guidelines

### 7.4 Performance Optimization
- Database indexes (verify all needed)
- Query optimization (EXPLAIN ANALYZE)
- Async operations where beneficial
- Caching strategies (if needed)
- Load testing (simulate heavy usage)

**Phase 7 Exit Criteria:**
- All validation criteria pass (see below)
- 80%+ test coverage
- Zero P0 bugs
- Documentation complete
- Performance acceptable (<5s for all operations)

---

## Validation & Acceptance Criteria

**MVP is complete when all criteria pass:**

### 1. Capture Workflow ✅
- Can capture 30 items in one day via CLI without friction
- Each capture takes < 5 seconds (including AI classification)
- AI correctly categorizes 90%+ of items (confidence >= 0.6)
- Malformed input handled gracefully (doesn't crash)

### 2. Triage Workflow ✅
- Can review and categorize all 30 items in under 10 minutes
- TUI panel with checkboxes is functional and responsive
- Bulk approval works (10+ items at once)
- Conversational modification works for edge cases
- Items move to correct folders, frontmatter updated

### 3. Review Workflow ✅
- Morning digest surfaces at configured time (7am default)
- Items resurface according to cadence rules
- Can defer items (tomorrow or user cadence)
- Can complete/archive items
- Transition to editing mode works

### 4. Editing Workflow ✅
- Can develop blog post from idea to draft using conversational agent
- Split-panel TUI shows live diffs
- Changes saved immediately on approval
- Conversation history preserved (checked in DB)
- Ambiguous instructions prompt clarifying questions

### 5. Sync Works Reliably ✅
- Can edit same item in CLI and Obsidian without data loss
- Conflicts detected and flagged for resolution
- Lock files prevent corruption
- External file moves handled (via item ID)
- Sync is fast (< 1 second to detect and update)

### 6. Emergent Taxonomy Works ✅
- System suggests new subcategory based on emerging patterns
- Tag promotion mechanism functional (detects clusters)
- User can approve/reject suggestions
- Approved subcategory created, items moved

---

## Next Steps After MVP

### Phase 8: Additional Surfaces
- Gnome applet
- Slack bot
- Web interface
- Mobile app

### Phase 9: Advanced Features
- Planning mode (project breakdown)
- Advanced search (filters, saved searches)
- Export/import (Notion, Obsidian, Roam)
- Collaboration (shared vaults)
- Scheduled surfacing (progressive throughout day)

### Phase 10: Cloud Migration
- Deploy to GCP Cloud Run
- Cloud SQL + pgvector
- Authentication (Firebase)
- Multi-tenancy (data isolation)
- Billing integration
