# Development Workflow Guide

This guide provides a comprehensive overview of development workflows, testing strategies, and quality tools for the Noosphere project.

## Quick Start

### Running Tests

**Python (api-service)**:
```bash
cd api-service

# Option 1: With activated venv
source .venv/bin/activate
pytest
deactivate

# Option 2: Using uv run (recommended, no activation needed)
uv run pytest

# With coverage
uv run pytest --cov=app --cov-fail-under=90

# Run specific test file
uv run pytest tests/models/test_user.py

# Run tests with markers
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
```

**Rust (cli + sync-service)**:
```bash
cd cli
cargo test

cd ../sync-service
cargo test

# Run specific test
cargo test test_config_deserialization

# Run with output
cargo test -- --nocapture
```

### Running Linters & Formatters

**Python (api-service)**:
```bash
cd api-service

# Format code (auto-fixes)
uv run ruff format app/

# Lint code (check for issues)
uv run ruff check app/

# Type checking
uv run pyright app/

# Run all quality checks
uv run ruff format app/ && uv run ruff check app/ && uv run pyright app/
```

**Rust (cli + sync-service)**:
```bash
cd cli

# Format check (rustfmt.toml configuration applied)
cargo fmt -- --check

# Format code (auto-fixes)
cargo fmt

# Linting with clippy
cargo clippy -- -D warnings

# Run all quality checks
cargo fmt --check && cargo clippy -- -D warnings

cd ../sync-service

# Same commands for sync-service
cargo fmt --check && cargo clippy -- -D warnings
```

## Testing Strategy

### Python (api-service)

**Test Types**:
- **Unit tests**: Fast, isolated, no external dependencies (marked with `@pytest.mark.unit`)
- **Integration tests**: Database interactions, API endpoint tests (marked with `@pytest.mark.integration`)
- **Slow tests**: Long-running tests (marked with `@pytest.mark.slow`)

**Test Structure**:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import get_db
from app.models.item import Item

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Database session fixture."""
    # Create test database session
    yield session
    # Cleanup

@pytest.mark.unit
def test_create_item(client: TestClient):
    """Test item creation endpoint."""
    response = client.post(
        "/api/items",
        json={"title": "Test", "content": "Content", "category": "ideas"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
    assert "id" in data
```

**Coverage Requirements**:
- Minimum coverage: 90%
- Configuration in `pyproject.toml`
- Run with: `uv run pytest --cov=app --cov-fail-under=90 --cov-report=term-missing`

**Test Organization**:
```
api-service/tests/
├── conftest.py           # Shared fixtures
├── api/                  # API endpoint tests
├── models/               # Model tests
├── db/                   # Database tests
└── services/             # Service logic tests
```

**Writing New Tests**:
1. Use existing fixtures from `conftest.py` (db_session, test_user, test_item)
2. Follow naming convention: `test_*.py`, `test_*()` functions
3. Add appropriate markers: `@pytest.mark.unit` or `@pytest.mark.integration`
4. Use descriptive test names that explain what is being tested
5. Aim for 90%+ coverage on new code

### Rust (cli + sync-service)

**Test Types**:
- **Unit tests**: `#[test]` functions in source files (inline with code)
- **Integration tests**: `tests/` directory (separate from source)
- **Doc tests**: Examples in documentation comments

**Test Structure**:

**Unit Tests (in source files)**:
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_deserialization() {
        let yaml = r#"
        vault:
          path: ~/test-vault
          watch_recursive: true
          debounce_ms: 500
        "#;

        let config: Config = serde_yaml::from_str(yaml).unwrap();
        assert!(config.vault.watch_recursive);
        assert_eq!(config.vault.debounce_ms, 500);
    }
}
```

**Integration Tests (in tests/ directory)**:
```rust
// tests/integration_test.rs
use noosphere_sync::config::Config;

#[test]
fn test_load_example_config() {
    let config = Config::load("config.example.yaml")
        .expect("Failed to load config");
    assert!(!config.vault.path.as_os_str().is_empty());
}
```

**Coverage Requirements**:
- Target: 80%+ coverage for Rust services
- Use `cargo-llvm-cov` for coverage analysis
- Install: `cargo install cargo-llvm-cov`
- Run: `cargo llvm-cov --html` (generates HTML report)

**Test Organization**:
```
cli/src/
├── app.rs              # Unit tests inline with #[cfg(test)]
├── handler.rs          # Unit tests inline
└── ui.rs              # Unit tests inline

cli/tests/
└── integration_test.rs # Integration tests

sync-service/src/
├── config.rs          # Unit tests inline
├── vault/
│   ├── lock.rs       # Unit tests inline
│   └── watcher.rs    # Unit tests inline

sync-service/tests/
└── config_test.rs    # Integration tests
```

**Writing New Tests**:
1. Add unit tests inline with code in `#[cfg(test)]` modules
2. Add integration tests in `tests/` directory for cross-module functionality
3. Use descriptive test names: `test_feature_behavior`
4. Use `Result<()>` return type for tests that can fail with context
5. Aim for 80%+ coverage on new code

## Code Quality Tools

### Python (api-service)

**Configuration**: All tool configs in `pyproject.toml`

**Ruff (Linting & Formatting)**:
- Linter configuration:
  - Line length: 100 characters
  - Target: Python 3.11+
  - Enabled checks: pycodestyle (E,W), pyflakes (F), isort (I), pep8-naming (N), pyupgrade (UP), flake8-bugbear (B), flake8-comprehensions (C4)
- Format code: `uv run ruff format app/`
- Check code: `uv run ruff check app/`
- Fix issues: `uv run ruff check --fix app/`

**Pyright (Type Checking)**:
- Configuration in `pyproject.toml`
- Mode: basic (balanced strictness)
- Check types: `uv run pyright app/`
- Tip: Add type hints to new code for better type safety

**Pytest (Testing)**:
- Configuration in `pyproject.toml`
- Test discovery: `test_*.py` files
- Markers: unit, integration, slow
- Run tests: `uv run pytest`
- Coverage: `uv run pytest --cov=app --cov-fail-under=90`

### Rust (cli + sync-service)

**Configuration**: `rustfmt.toml` in each service directory

**Rustfmt (Formatting)**:
- Configuration:
  - Max width: 100 characters
  - Edition: 2021
  - Tab spaces: 4
  - Reorder imports/modules: enabled
- Format check: `cargo fmt -- --check`
- Format code: `cargo fmt`

**Clippy (Linting)**:
- Rust's official linter
- Run with warnings as errors: `cargo clippy -- -D warnings`
- Fix suggestions: `cargo clippy --fix`
- Tip: Clippy provides excellent suggestions for idiomatic Rust

**Cargo Test (Testing)**:
- Built-in test runner
- Run tests: `cargo test`
- Run with output: `cargo test -- --nocapture`
- Run specific test: `cargo test test_name`

**Cargo Llvm-Cov (Coverage)**:
- Install: `cargo install cargo-llvm-cov`
- HTML report: `cargo llvm-cov --html`
- Terminal report: `cargo llvm-cov --lcov`
- Target: 80%+ coverage

## Git Workflow

**This project uses Git-Flow branching model.**

### Branch Types

- `main` - Production releases only (tagged with versions)
- `develop` - Integration branch (base for all feature work)
- `feature/*` - Feature development branches (from develop)
- `release/*` - Release preparation branches (from develop)
- `hotfix/*` - Emergency fixes (from main)

### Branch Naming Convention

```bash
feature/EPIC-X-Y-brief-description   # Feature branches
release/v1.0.0                       # Release branches
hotfix/fix-critical-bug              # Hotfix branches
```

### Development Process

**Starting a new feature**:
```bash
# Ensure develop is up to date
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/EPIC-2-3-add-classification

# Make changes, commit regularly
git add .
git commit -m "feat(ai): add classification service"

# Push feature branch
git push -u origin feature/EPIC-2-3-add-classification
```

**Keeping feature branch updated**:
```bash
# Fetch latest changes
git fetch origin

# Update local develop
git checkout develop
git pull origin develop

# Merge develop into feature branch
git checkout feature/EPIC-2-3-add-classification
git merge develop

# Resolve any conflicts, then push
git push origin feature/EPIC-2-3-add-classification
```

**Completing a feature**:
```bash
# Create pull request via GitHub CLI
gh pr create \
  --title "[EPIC-2-3] Add AI classification service" \
  --body "Description of changes" \
  --base develop

# After PR approval, merge to develop (done via GitHub UI or CLI)
# Delete feature branch after merge
git checkout develop
git pull origin develop
git branch -d feature/EPIC-2-3-add-classification
```

### Commit Message Format

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config)

**Examples**:
```
feat(api): add item classification endpoint

Implements AI-powered classification using litellm.
Supports Gemini, OpenAI, and Anthropic models.

Closes #42

---

fix(cli): handle empty search results gracefully

Previously crashed when no results found.
Now displays user-friendly message.

---

test(db): add integration tests for item CRUD

Adds tests for create, read, update, delete operations.
Uses test database fixtures from conftest.py.
Coverage: 95%
```

## Code Review Checklist

### Functionality
- [ ] Code implements the requirements from the GitHub issue
- [ ] Edge cases are handled appropriately
- [ ] Error handling is robust and informative
- [ ] No hardcoded values that should be configurable
- [ ] No security vulnerabilities (SQL injection, XSS, etc.)

### Quality
- [ ] Code follows project conventions (see `AGENTS.md` for each service)
- [ ] Variable and function names are descriptive
- [ ] Complex logic has explanatory comments
- [ ] No commented-out code (use git history instead)
- [ ] No debug print statements or console.logs left in code

### Testing
- [ ] New code has unit tests
- [ ] Integration tests added for API changes
- [ ] Tests cover happy path and error cases
- [ ] Coverage meets minimum threshold (90% Python, 80% Rust)
- [ ] All tests pass locally

### Documentation
- [ ] API changes documented in AGENTS.md
- [ ] Complex functionality has docstrings/comments
- [ ] README updated if user-facing changes
- [ ] Migration guide provided if breaking changes

### Git
- [ ] Commit messages follow conventional format
- [ ] Commits are logical units of work
- [ ] Branch name follows convention (feature/EPIC-X-Y-description)
- [ ] No merge conflicts with develop branch

### Quality Gates
- [ ] All linters pass (ruff/rustfmt)
- [ ] All type checks pass (pyright for Python)
- [ ] All clippy warnings addressed (Rust)
- [ ] All tests pass with required coverage

## Pre-Commit Setup (Optional)

Pre-commit hooks can automatically run quality checks before each commit.

**Installation** (Python):
```bash
cd api-service
uv pip install pre-commit
pre-commit install
```

This will run ruff format, ruff check, and pyright before each commit.

For Rust services, consider using `cargo-husky` or manual git hooks.

## Troubleshooting

### Python (api-service)

**Issue**: `pytest: command not found`
```bash
# Solution: Use uv run or activate venv
uv run pytest

# Or activate venv first
source .venv/bin/activate
pytest
```

**Issue**: `ruff: command not found`
```bash
# Solution: Install with uv
uv pip install ruff

# Or use uv run
uv run ruff check app/
```

**Issue**: Type errors from pyright
```bash
# Solution: Add type hints or use # type: ignore for third-party issues
def process_item(item: Item) -> dict[str, Any]:
    return item.dict()  # type: ignore[attr-defined]
```

### Rust (cli + sync-service)

**Issue**: `cargo fmt` not using rustfmt.toml
```bash
# Solution: Ensure rustfmt.toml is in the service root directory
# Check with:
ls -la cli/rustfmt.toml
ls -la sync-service/rustfmt.toml
```

**Issue**: Clippy warnings failing CI
```bash
# Solution: Fix all warnings or explicitly allow them
#![allow(clippy::warning_name)]  // At file level

// Or for specific items
#[allow(clippy::warning_name)]
fn my_function() {}
```

**Issue**: Tests fail with "file not found"
```bash
# Solution: Ensure working directory is correct
cd cli  # or sync-service
cargo test

# For integration tests, check paths are relative to project root
```

## Resources

### Python/FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pytest Documentation](https://docs.pytest.org)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pyright Documentation](https://github.com/microsoft/pyright)

### Rust
- [Rust Book](https://doc.rust-lang.org/book/)
- [Cargo Book](https://doc.rust-lang.org/cargo/)
- [Clippy Lints](https://rust-lang.github.io/rust-clippy/)
- [Rustfmt Configuration](https://rust-lang.github.io/rustfmt/)

### Project Documentation
- `docs/agents/standards.md` - Comprehensive coding standards
- `docs/agents/architecture.md` - System architecture overview
- `docs/setup.md` - Initial project setup
- `docs/github-workflow.md` - GitHub workflow and PR process
- Service-specific `AGENTS.md` files - Context for each service

## Next Steps

1. **Before writing code**: Read the appropriate `AGENTS.md` file for service context
2. **During development**: Run quality checks frequently (`ruff check`, `cargo clippy`)
3. **Before committing**: Run all tests and ensure coverage meets thresholds
4. **Before creating PR**: Review this checklist and verify all quality gates pass
