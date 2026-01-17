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

## Quick Start

### Prerequisites

- Python 3.14+
- Rust 1.70+
- PostgreSQL 14+ with pgvector extension
- uv (Python package manager)
- AI API key (Gemini, OpenAI, or Anthropic)

### Installation

```bash
# Clone repository
git clone git@github.com:deserat/noosphere.git
cd noosphere

# Set up Python environment (API Service)
cd api-service
uv venv
source .venv/bin/activate
uv sync
alembic upgrade head
cd ..

# Build Rust binaries (CLI + Sync Service)
cd cli
cargo build --release
cd ../sync-service
cargo build --release
cd ..

# Configure environment
cp .env.example .env
# Edit .env with your database URL and AI API keys

# Start services
./start.sh
```

**Note**: See [docs/setup.md](docs/setup.md) for detailed setup instructions including uv installation.

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
