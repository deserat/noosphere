# Development Setup Guide

This guide walks you through setting up the Noosphere development environment on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Python 3.14+**: Backend API service
  ```bash
  python3 --version  # Should be 3.14 or higher
  ```

- **uv**: Python package manager (replaces pip/venv)
  ```bash
  # Install uv
  # macOS/Linux:
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows:
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

  # Or via package managers:
  brew install uv           # macOS (Homebrew)
  winget install astral-sh.uv  # Windows (WinGet)

  # Verify installation
  uv --version
  ```

- **Rust 1.70+**: CLI and sync service
  ```bash
  rustc --version    # Should be 1.70 or higher
  cargo --version
  ```

- **PostgreSQL 14+**: Database with pgvector extension
  ```bash
  psql --version     # Should be 14 or higher
  ```

- **Git**: Version control
  ```bash
  git --version
  ```

### Optional Tools

- **Docker**: For containerized PostgreSQL (recommended for development)
- **psql**: PostgreSQL command-line client
- **jq**: JSON parsing for API testing

## Step 1: Clone Repository

```bash
git clone git@github.com:deserat/noosphere.git
cd noosphere
```

## Step 2: PostgreSQL Setup

### Option A: Docker (Recommended)

```bash
# Pull PostgreSQL with pgvector
docker pull ankane/pgvector

# Run PostgreSQL container
docker run -d \
  --name noosphere-db \
  -e POSTGRES_USER=noosphere_user \
  -e POSTGRES_PASSWORD=dev_password \
  -e POSTGRES_DB=noosphere \
  -p 5432:5432 \
  ankane/pgvector

# Verify connection
docker exec -it noosphere-db psql -U noosphere_user -d noosphere -c "SELECT version();"
```

### Option B: Local PostgreSQL Installation

#### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install pgvector
sudo apt install postgresql-14-pgvector

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS (Homebrew)

```bash
# Install PostgreSQL
brew install postgresql@14

# Install pgvector
brew install pgvector

# Start PostgreSQL
brew services start postgresql@14
```

#### Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In psql:
CREATE USER noosphere_user WITH PASSWORD 'dev_password';
CREATE DATABASE noosphere OWNER noosphere_user;
\c noosphere
CREATE EXTENSION vector;
\q
```

## Step 3: Python Environment Setup

### Create Virtual Environment

```bash
cd api-service

# Create virtual environment (creates .venv/ directory)
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows
```

### Install Dependencies

```bash
# Install Python packages from requirements.txt using uv
uv pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import sqlalchemy; import litellm; import pgvector; print('✓ All Python packages installed')"

# Or use uv run (no activation needed)
uv run python -c "import fastapi; import sqlalchemy; import litellm; import pgvector; print('✓ All Python packages installed')"
```

**Note**: We use `requirements.txt` with version pinning (format: `>=X.Y.Z,<X.(Y+1).0`) to ensure stable, reproducible dependencies across all development environments.

### Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Required variables:
# - DATABASE_URL=postgresql://noosphere_user:dev_password@localhost:5432/noosphere
# - VAULT_PATH=~/noosphere-vault
# - API_HOST=127.0.0.1
# - API_PORT=8000
# Optional (for AI features):
# - GEMINI_API_KEY=your-key
# - OPENAI_API_KEY=your-key
```

### Run Database Migrations

```bash
# Apply migrations to create database schema
alembic upgrade head

# Verify tables created
psql -U noosphere_user -d noosphere -c "\dt"
```

### Verify API Service

```bash
# Test import
python -c "from app.main import app; print('✓ API service ready')"

# Deactivate virtual environment (when done)
deactivate
```

## Step 4: Rust Environment Setup

### Install Rust (if not already installed)

```bash
# Install via rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Reload environment
source $HOME/.cargo/env

# Verify installation
rustc --version
cargo --version
```

### Build CLI (ratatui TUI)

```bash
cd cli

# Check project compiles
cargo check

# Build in debug mode
cargo build

# Run CLI (Phase 1: just verifies compilation)
cargo run

# Expected output:
# "Noosphere CLI - Elm Architecture TUI"
# "✓ Rust toolchain verified"
# "✓ ratatui dependencies ready"
```

### Build Sync Service

```bash
cd ../sync-service

# Check project compiles
cargo check

# Build in debug mode
cargo build

# Run sync service (Phase 1: just verifies compilation)
cargo run

# Expected output:
# "Noosphere Sync Service - Development"
# "Async runtime verified"
```

## Step 5: Create File Vault

```bash
# Create vault directory
mkdir -p ~/noosphere-vault/{ideas,tasks,notes,resources,journal}

# Verify structure
ls -la ~/noosphere-vault
```

## Step 6: Verify Complete Setup

### Test API Service

```bash
cd api-service
source venv/bin/activate

# Start API service
python -m app.main

# In another terminal, test health endpoint
curl http://localhost:8000/api/health | jq

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "...",
#   "database": "connected",
#   "scheduler": "running",
#   "version": "0.1.0"
# }

# Stop server: Ctrl+C
deactivate
```

### Test Rust Projects

```bash
# CLI
cd cli
cargo test
cargo run

# Sync Service
cd ../sync-service
cargo test
cargo run
```

### Run All Tests

```bash
# Python tests
cd api-service
source .venv/bin/activate
pytest
deactivate

# Or use uv run (no activation needed)
uv run pytest

# Rust tests
cd ../cli
cargo test

cd ../sync-service
cargo test
```

## Platform-Specific Notes

### Linux

- PostgreSQL typically runs on port 5432
- Virtual environment activation: `source .venv/bin/activate`
- uv installation: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Vault path: `~/noosphere-vault`

### macOS

- PostgreSQL installed via Homebrew uses `/opt/homebrew/var/postgresql@14`
- Virtual environment activation: `source .venv/bin/activate`
- uv installation: `brew install uv` (Homebrew) or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Vault path: `~/noosphere-vault`

### Windows

- PostgreSQL runs as Windows service
- Virtual environment activation: `.venv\Scripts\activate`
- uv installation: `winget install astral-sh.uv` or PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Vault path: `%USERPROFILE%\noosphere-vault`

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                # macOS

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log  # Linux
tail -f /opt/homebrew/var/log/postgresql@14.log          # macOS

# Test connection manually
psql -U noosphere_user -d noosphere -h localhost
```

### Python Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf .venv
uv venv
source .venv/bin/activate
uv sync
```

### Rust Compilation Issues

```bash
# Update Rust toolchain
rustup update

# Clean build artifacts
cargo clean

# Rebuild
cargo build
```

**OpenSSL System Dependency Issues**:

If you encounter OpenSSL-related errors during Rust compilation (common on Linux without `libssl-dev`), the project is already configured to use `rustls` (pure Rust TLS implementation) instead of native OpenSSL. This configuration is in both `cli/Cargo.toml` and `sync-service/Cargo.toml`:

```toml
# Uses rustls instead of native-tls to avoid OpenSSL system dependency
reqwest = { version = "0.11", features = ["json", "rustls-tls"], default-features = false }
```

If you still encounter TLS issues, verify that your Cargo.toml files have `default-features = false` to disable native-tls.

### Database Migration Issues

```bash
# Check migration status
alembic current

# Rollback and retry
alembic downgrade -1
alembic upgrade head

# Reset database (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head
```

## Next Steps

Once your environment is set up:

1. Review [Implementation Roadmap](project/implementation-roadmap.md) to understand development phases
2. Check [User Stories](project/stories/README.md) for current sprint work
3. Read [Multi-Agent Workflow](agents/README.md) for collaborative development patterns
4. Start with Phase 1 stories (repository structure, database, configuration)

## Development Workflow

### Git-Flow Branching Model

**This project uses Git-Flow for branch management.**

**Branch Structure**:
- `main` - Production releases only (tagged with versions)
- `develop` - Integration branch for all features
- `feature/*` - Feature branches (from develop)
- `release/*` - Release preparation (from develop)
- `hotfix/*` - Emergency production fixes (from main)

See [agents/standards.md](agents/standards.md#git-workflow) for complete git-flow documentation.

### Starting Work on a Feature

```bash
# 1. Start from develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/EPIC-1-2-dev-environments

# 3. Activate Python environment (if working on API)
cd api-service
source .venv/bin/activate

# 4. Run migrations (if database schema changed)
alembic upgrade head

# 5. Start services
# Terminal 1: API Service
python -m app.main

# Terminal 2: Sync Service (when implemented)
cd sync-service
cargo run

# Terminal 3: CLI (when implemented)
cd cli
cargo run
```

### Committing and Merging

```bash
# Make changes and commit regularly
git add .
git commit -m "feat(api): add health check endpoint"

# Keep feature branch updated with develop
git checkout develop
git pull origin develop
git checkout feature/EPIC-1-2-dev-environments
git merge develop

# When feature is complete, merge back to develop
git checkout develop
git pull origin develop
git merge --no-ff feature/EPIC-1-2-dev-environments
git push origin develop

# Delete feature branch
git branch -d feature/EPIC-1-2-dev-environments
```

### Running Tests Before Commit

```bash
# Python tests
cd api-service
source .venv/bin/activate
pytest
deactivate

# Or use uv run (recommended, no activation needed)
cd api-service
uv run pytest

# Rust tests
cd cli
cargo test

cd ../sync-service
cargo test
```

### Code Quality Checks

```bash
# Python quality checks (when configured)
cd api-service
source .venv/bin/activate
ruff check .
ruff format --check .
pyright

# Or use uv run (recommended, no activation needed)
cd api-service
uv run ruff check .
uv run ruff format --check .
uv run pyright

# Rust formatting and linting
cd cli
cargo fmt --check
cargo clippy
```

## Getting Help

- Check [GitHub Issues](https://github.com/deserat/noosphere/issues) for known problems
- Review story files in `docs/project/stories/` for implementation details
- Consult `AGENTS.md` files in each service directory for service-specific context
