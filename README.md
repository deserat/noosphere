# Noosphere

Personal knowledge management system with frictionless capture, AI classification, and proactive surfacing.

## Vision

Noosphere is your **Second Brain** - a personal knowledge management system designed to capture fleeting thoughts and ideas effortlessly, classify them intelligently using AI, and surface them back to you at the right moment.

### Core Principles

- **Frictionless Capture**: Sub-second capture time. No friction between thought and storage.
- **AI-Powered Intelligence**: Automatic classification, tagging, and relationship discovery
- **Proactive Surfacing**: Intelligent reminders based on context, cadence, and relevance
- **Local-First**: Your knowledge stays on your machine in portable markdown format
- **Tool Agnostic**: File-based vault works with Obsidian, VS Code, or any markdown editor

## Architecture Overview

Noosphere follows a clean client/server architecture with three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer (Rust)                      │
├─────────────────────────┬───────────────────────────────────┤
│  CLI (ratatui TUI)      │  Sync Service (File Watching)     │
│  - Frictionless capture │  - Monitors vault changes         │
│  - Quick entry          │  - Bi-directional sync with API   │
│  - Elm Architecture     │  - Event-driven async processing  │
└─────────────┬───────────┴───────────────┬───────────────────┘
              │                           │
              └───────────────┬───────────┘
                              │
                    ┌─────────▼─────────┐
                    │   REST API (HTTP) │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│              Server Layer (Python/FastAPI)                     │
├────────────────────────────────────────────────────────────────┤
│  API Service                                                   │
│  - REST endpoints for CRUD operations                          │
│  - AI classification (litellm → Gemini/Claude/GPT)             │
│  - Background scheduler for surfacing jobs                     │
│  - Health monitoring and observability                         │
└────────────────┬───────────────────────────────┬───────────────┘
                 │                               │
        ┌────────▼────────┐            ┌────────▼────────┐
        │  PostgreSQL +   │            │  File Vault     │
        │  pgvector       │            │  (Markdown)     │
        │  - 9 tables     │            │  - YAML         │
        │  - Vector       │            │    frontmatter  │
        │    embeddings   │            │  - Categories   │
        └─────────────────┘            └─────────────────┘
```

### Technology Stack

**Backend (Python)**:
- FastAPI for REST API with `app/` standard layout
- SQLAlchemy for ORM and database migrations
- PostgreSQL 14+ with pgvector for semantic search
- litellm for multi-provider AI integration
- APScheduler for background jobs

**Client (Rust)**:
- CLI: ratatui (Elm Architecture TUI) for terminal interface
- Sync Service: notify for file watching, tokio for async runtime
- reqwest for HTTP client communication with API

**Data Storage**:
- PostgreSQL: Relational data with vector embeddings
- File Vault: Markdown files with YAML frontmatter at `~/.noosphere-vault`

### Architecture Patterns

- **API Service**: FastAPI with `app/` layout (api/endpoints/, core/, db/, models/, schemas/, crud/, services/)
- **CLI**: Elm Architecture (Model-Update-View) with ratatui for TUI
- **Sync Service**: Event-driven file watching with async Rust

## Dependencies

### System Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.14+ | API service runtime |
| **Rust** | 1.70+ | CLI and sync service compilation |
| **PostgreSQL** | 14+ | Primary database |
| **uv** | Latest | Python package manager (replaces pip/venv) |
| **Git** | Latest | Version control |

### Development Tools

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# OR
brew install uv  # macOS Homebrew

# Install Rust (if not installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install PostgreSQL + pgvector
brew install postgresql@14 pgvector  # macOS
# OR
sudo apt install postgresql-14 postgresql-14-pgvector  # Ubuntu/Debian
```

### Python Dependencies (API Service)

**Core Frameworks**:
- `fastapi` (0.104+) - Web framework with automatic API documentation
- `uvicorn` (0.24+) - ASGI server for production deployment
- `sqlalchemy` (2.0+) - ORM for database operations
- `alembic` (1.12+) - Database migration tool

**Database**:
- `psycopg2-binary` (2.9+) - PostgreSQL adapter
- `pgvector` (0.2.4+) - Vector similarity search extension

**AI Integration**:
- `litellm` (1.0+) - Unified interface for multiple LLM providers (OpenAI, Anthropic, Google)

**Utilities**:
- `pydantic` (2.5+) - Data validation and settings management
- `python-dotenv` (1.0+) - Environment variable management
- `pyyaml` (6.0+) - YAML configuration parsing
- `watchdog` (3.0+) - File system monitoring

**Development**:
- `pytest` (7.4+) - Testing framework
- `pytest-asyncio` (0.21+) - Async test support
- `ruff` (0.1+) - Fast Python linter and formatter

See [`api-service/requirements.txt`](api-service/requirements.txt) for complete list with version pinning.

### Rust Dependencies

**CLI (ratatui TUI)**:
- `ratatui` (0.26) - Terminal UI framework
- `crossterm` (0.27) - Cross-platform terminal manipulation
- `tokio` (1.35) - Async runtime
- `reqwest` (0.11) - HTTP client with rustls-tls (pure Rust TLS)
- `clap` (4.4) - Command-line argument parsing
- `serde` (1.0) - Serialization framework
- `tracing` (0.1) - Logging and instrumentation

**Sync Service**:
- `tokio` (1.35) - Async runtime for non-blocking I/O
- `notify` (6.1) - File system event monitoring
- `reqwest` (0.11) - HTTP client for API communication
- `serde` (1.0) - JSON/YAML serialization
- `sha2` (0.10) - Content hashing for change detection
- `config` (0.14) - Configuration management

See [`cli/Cargo.toml`](cli/Cargo.toml) and [`sync-service/Cargo.toml`](sync-service/Cargo.toml) for complete dependency specifications.

### Database Extensions

**PostgreSQL Extensions**:
- `pgvector` - Vector similarity search for semantic embeddings
  ```sql
  CREATE EXTENSION vector;
  ```

### Optional Dependencies

**For AI Features** (Phase 2+):
- Gemini API key (Google AI)
- OpenAI API key (GPT models)
- Anthropic API key (Claude models)

**For Development**:
- `jq` - JSON parsing for API testing
- `docker` - Containerized PostgreSQL (alternative to local install)
- `psql` - PostgreSQL command-line client

### Installation Verification

After installing dependencies, verify with:

```bash
# Check versions
python3 --version    # Should be 3.14+
uv --version         # Should be latest
cargo --version      # Should be 1.70+
psql --version       # Should be 14+

# Verify Python environment
cd api-service
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
python -c "import fastapi; import sqlalchemy; import litellm; print('✓')"

# Verify Rust compilation
cd ../cli && cargo build && echo "✓ CLI compiles"
cd ../sync-service && cargo build && echo "✓ Sync service compiles"
```

## Quick Start

### Prerequisites

See the [Dependencies](#dependencies) section above for complete system requirements and installation instructions.

**Quick checklist**:
- ✓ Python 3.14+, Rust 1.70+, PostgreSQL 14+, uv installed
- ✓ pgvector extension available
- ✓ AI API key (optional for Phase 1, required for AI features)

### Installation

```bash
# Clone repository
git clone git@github.com:deserat/noosphere.git
cd noosphere

# Set up Python environment (API Service)
cd api-service
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
alembic upgrade head  # Apply database migrations
cd ..

# Build Rust binaries (CLI + Sync Service)
cd cli
cargo build --release
cd ../sync-service
cargo build --release
cd ..

# Configure environment variables
cp .env.example .env
# Edit .env with your database URL and AI API keys

# Start services
./start.sh
```

**Note**: See [docs/setup.md](docs/setup.md) for detailed platform-specific setup instructions, troubleshooting, and development workflow.

### First Capture

```bash
# Launch CLI
./cli/target/release/noosphere

# Quick capture (press 'c')
> "Idea for weekend project: build a home automation dashboard"

# CLI automatically:
# 1. Saves to vault as markdown
# 2. Triggers sync service
# 3. API classifies with AI
# 4. Schedules surfacing based on cadence
```

## Project Structure

```
noosphere/
├── cli/                    # Rust CLI (ratatui TUI with Elm Architecture)
│   ├── src/
│   │   ├── main.rs        # Event loop
│   │   ├── app.rs         # Model (application state)
│   │   ├── ui.rs          # View (rendering)
│   │   ├── handler.rs     # Update (event handlers)
│   │   ├── event.rs       # Event types
│   │   ├── tui.rs         # Terminal setup
│   │   ├── components/    # Reusable UI components
│   │   └── api/           # API client
│   └── tests/
├── api-service/            # Python FastAPI backend
│   ├── app/               # Main application package
│   │   ├── api/endpoints/ # Route handlers
│   │   ├── core/          # Configuration, security
│   │   ├── db/            # Database session, base
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response
│   │   ├── crud/          # Database operations
│   │   ├── services/      # Business logic (AI, scheduler)
│   │   └── vault/         # Markdown utilities
│   ├── migrations/        # Alembic migrations
│   └── tests/
├── sync-service/           # Rust file watching service
│   ├── src/
│   └── tests/
└── docs/                   # Documentation
    ├── setup.md           # Development setup guide
    ├── agents/            # Multi-agent workflow docs
    └── project/           # Project roadmap and stories
```

## Development

### Running Tests

```bash
# API Service (Python)
cd api-service
pytest

# CLI (Rust)
cd cli
cargo test

# Sync Service (Rust)
cd sync-service
cargo test
```

### Database Migrations

```bash
cd api-service
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Documentation

- [Setup Guide](docs/setup.md) - Step-by-step local environment setup
- [Implementation Roadmap](docs/project/implementation-roadmap.md) - Development phases and milestones
- [User Stories](docs/project/stories/README.md) - Agile user stories and epics
- [Multi-Agent Workflow](docs/agents/README.md) - Collaborative development guide

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Repository structure and documentation
- ⏳ Development environments (Python + Rust)
- ⏳ PostgreSQL + pgvector setup
- ⏳ File vault structure
- ⏳ Basic service scaffolding

### Phase 2: AI Classification
- AI-powered item classification
- Automatic categorization and tagging
- Embedding generation and semantic search
- CLI capture interface

### Phase 3: Surfacing & Intelligence
- Cadence-based surfacing
- Context-aware surfacing triggers
- Related item discovery
- Proactive notifications

### Phase 4: Polish & Distribution
- Cross-platform installers
- Performance optimization
- Documentation and tutorials
- Community feedback integration

## Contributing

This is a personal project, but feedback and suggestions are welcome via GitHub issues.

### Git Workflow

This project uses **Git-Flow** branching model:

- **main**: Production-ready code (tagged releases)
- **develop**: Integration branch for features (base for all development)
- **feature/**: Feature branches (from develop)
- **release/**: Release preparation (from develop)
- **hotfix/**: Emergency production fixes (from main)

See [docs/agents/standards.md](docs/agents/standards.md#git-workflow) for complete git-flow documentation.

## License

MIT License - See LICENSE file for details

## Contact

GitHub: [@deserat](https://github.com/deserat)
