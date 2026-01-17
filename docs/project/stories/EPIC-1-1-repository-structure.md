# Repository Structure and Documentation Framework

**Epic**: Development Environment Setup
**Priority**: P0
**Story Points**: 3

## User Story

As a developer,
I need a well-organized repository structure with clear documentation,
So that the team can navigate the codebase, understand architectural decisions, and onboard efficiently.

## Acceptance Criteria

- [ ] Root directory structure created with clean service separation:
  - `cli/` (Rust client application)
  - `api-service/` (Python API + AI + Scheduler)
  - `sync-service/` (Rust file watching service)
  - `docs/` (Project documentation)
- [ ] API service subdirectories following FastAPI conventions:
  - `app/` (main application package)
    - `api/` (API routes)
      - `endpoints/` (route handlers)
    - `core/` (configuration, security)
    - `db/` (database session, base)
    - `models/` (SQLAlchemy ORM models)
    - `schemas/` (Pydantic request/response models)
    - `crud/` (database operations)
    - `services/` (business logic: AI, scheduler)
    - `vault/` (markdown utilities)
  - `migrations/` (Alembic database migrations)
  - `tests/` (pytest test suite)
- [ ] Sync service subdirectories created:
  - `src/`, `tests/`
- [ ] CLI subdirectories following Elm Architecture (ratatui TUI pattern):
  - `src/` (application source)
    - `main.rs` (entry point, event loop)
    - `app.rs` (App struct - Model)
    - `ui.rs` (rendering logic - View)
    - `event.rs` (event types and polling)
    - `handler.rs` (message handlers - Update)
    - `tui.rs` (terminal setup/teardown)
    - `components/` (reusable UI widgets)
    - `api/` (API client for backend communication)
  - `tests/` (integration tests)
- [ ] Git repository initialized with comprehensive `.gitignore`:
  - Python: `__pycache__`, `*.pyc`, `venv/`, `.pytest_cache`
  - Rust: `target/`, `Cargo.lock` (for binaries)
  - IDE: `.vscode/`, `.idea/`
  - Environment: `.env`, `.env.local`
- [ ] Top-level README.md created with:
  - Project vision and goals
  - Architecture overview
  - Quick start instructions
  - Links to detailed documentation
- [ ] Development setup guide created at `docs/setup.md`:
  - Prerequisites (PostgreSQL, Rust, Python versions)
  - Step-by-step local environment setup
  - How to run tests
  - How to start services
- [ ] Multi-agent development context established:
  - `docs/agents/` directory created
  - `docs/agents/README.md` (multi-agent workflow overview)
  - `docs/agents/architecture.md` (system-wide architectural decisions)
  - `docs/agents/standards.md` (Python and Rust coding standards)
  - `AGENTS.md` in each service directory (service-specific context and boundaries)

## Technical Notes

**Architecture Decisions**:
- Clean client/server separation: No shared code between services
- Server (Python): API + AI + integrated scheduler (FastAPI conventions)
- Client (Rust): CLI TUI using Elm Architecture + sync-service (both local)
- Each service is independently deployable and testable

**CLI Elm Architecture Pattern**:
The CLI follows the Elm Architecture (Model-Update-View):
- **Model** (`app.rs`): Application state (current view, input buffers, selected items)
- **Update** (`handler.rs`): State transitions based on events (key presses, API responses)
- **View** (`ui.rs`): Render state to terminal using ratatui widgets
- **Event Loop** (`main.rs`): Poll events → Update state → Render view → Repeat

This provides:
- **Predictable state management**: All state changes go through handlers
- **Testable logic**: Pure functions for state updates
- **Composable UI**: Reusable components in `components/`
- **Clean separation**: UI rendering separate from business logic

**Directory Naming Conventions**:
- Kebab-case for directories (e.g., `api-service`, not `api_service` or `ApiService`)
- Services named by function, not technology
- Tests colocated with implementation in each service

**AGENTS.md Purpose**:
- Provides context for AI coding assistants working on specific services
- Defines boundaries and responsibilities for each service
- Documents service-specific patterns and conventions
- Enables parallel development by multiple AI agents

**Git Strategy**:
- Monorepo structure (all services in one repository)
- Each service can be versioned independently if needed
- `.gitignore` prevents committing build artifacts, dependencies, IDE configs

## Dependencies

- **Blocks**:
  - EPIC-1-2 (Development environments need directory structure)
  - EPIC-2-1 (Database setup needs migrations directory)
  - EPIC-3-1 (Vault utilities need app/vault directory)
  - EPIC-4-1 (Configuration needs app/core directory)
  - EPIC-5-1 (Service scaffolding needs all directories)
- **Blocked By**: None (this is the first task)
- **Related**: All other Phase 1 stories depend on this foundation

## Verification

**Manual Checks**:
```bash
# Verify directory structure
ls -la
# Should show: cli/, api-service/, sync-service/, docs/, .git/, .gitignore, README.md

# Verify api-service structure
ls -la api-service/
# Should show: app/, migrations/, tests/, config.yaml (will be added later), requirements.txt (will be added later)

# Verify FastAPI app structure
ls -la api-service/app/
# Should show: api/, core/, db/, models/, schemas/, crud/, services/, vault/

# Verify CLI Elm Architecture structure
ls -la cli/src/
# Should show: main.rs, app.rs, ui.rs, event.rs, handler.rs, tui.rs, components/, api/

# Verify sync service structure
ls -la sync-service/src/
# Should show: main.rs, config.rs, watcher.rs, sync.rs, api.rs

# Verify git initialization
git status
# Should show initialized repository

# Verify .gitignore works
touch api-service/__pycache__/test.pyc
touch cli/target/debug/test
git status
# Should NOT show __pycache__ or target/ directories
rm -rf api-service/__pycache__ cli/target/
```

**Documentation Quality**:
- [ ] README.md is clear and provides enough context for a new developer to understand the project
- [ ] docs/setup.md has step-by-step instructions that can be followed without prior knowledge
- [ ] AGENTS.md files clearly define service boundaries and responsibilities
- [ ] docs/agents/ documentation explains multi-agent development workflow

**Completion Criteria**:
- All directory structures exist as specified
- Git repository initialized and .gitignore working
- Documentation files created and contain meaningful content (not placeholders)
- A new team member can clone the repo and understand the project structure
