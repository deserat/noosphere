# Development Tooling and Quality Gates

**Epic**: Development Environment Setup
**Priority**: P2
**Story Points**: 3

## User Story

As a developer,
I need automated code quality tools and testing infrastructure,
So that the codebase maintains consistent style, catches errors early, and supports continuous integration.

## Acceptance Criteria

### Python Tooling (API Service)
- [ ] `pytest.ini` created with test configuration:
  ```ini
  [pytest]
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  addopts = -v --tb=short --strict-markers
  markers =
      unit: Unit tests
      integration: Integration tests
      slow: Slow running tests
  ```
- [ ] Linting configuration created (choose one):
  - **Option A**: `.flake8` for Flake8
  - **Option B**: `ruff.toml` for Ruff (faster, recommended)
- [ ] `pyproject.toml` created with formatting configuration:
  ```toml
  [tool.black]
  line-length = 100
  target-version = ['py311']
  include = '\.pyi?$'
  exclude = '''
  /(
      \.git
    | \.venv
    | venv
    | \.pytest_cache
    | __pycache__
  )/
  '''

  [tool.isort]
  profile = "black"
  line_length = 100
  ```
- [ ] Linting and formatting commands documented in docs/development.md
- [ ] Sample unit test created in api-service/tests/test_sample.py to verify pytest works

### Rust Tooling (CLI + Sync Service)
- [ ] `rustfmt.toml` created for code formatting:
  ```toml
  max_width = 100
  edition = "2021"
  ```
- [ ] `clippy.toml` created for linting configuration (if needed for custom rules)
- [ ] Sample tests created:
  - cli/src/main.rs: Simple `#[test]` function
  - sync-service/src/main.rs: Simple `#[test]` function
- [ ] Test commands verified:
  ```bash
  cargo test
  cargo clippy
  cargo fmt --check
  ```

### Pre-commit Hooks (Optional for MVP)
- [ ] `.pre-commit-config.yaml` created (if implementing):
  - Python: black, isort, flake8/ruff
  - Rust: cargo fmt, cargo clippy
  - General: trailing whitespace, end of file
- [ ] Pre-commit installation instructions in docs/setup.md
- **Note**: Mark as optional if time-constrained; can be added later

### Development Workflow Documentation
- [ ] `docs/development.md` created with:
  - How to run tests (Python and Rust)
  - How to run linters/formatters
  - Code review checklist
  - Git workflow (branch naming, commit messages)
  - Pull request template guidelines
- [ ] Testing strategy documented:
  - Unit tests: Fast, isolated, no external dependencies
  - Integration tests: Test service interactions, use test database
  - When to write each type of test

## Technical Notes

**Python Tool Choices**:
- **Ruff** (recommended): Faster than Flake8, combines linting + formatting
- **Black**: Opinionated formatter, reduces bike-shedding
- **isort**: Import statement formatting
- **pytest**: Industry standard testing framework

**Rust Tool Choices**:
- **rustfmt**: Official Rust formatter (cargo fmt)
- **clippy**: Official Rust linter (cargo clippy)
- Built-in: `cargo test` for testing

**Test Structure**:
- Python: Separate `tests/` directory with `test_*.py` files
- Rust: Tests in-line with `#[test]` or separate `tests/` directory

**Quality Targets** (not enforced in Phase 1, but documented):
- Test coverage: Aim for 80%+ for core logic
- Linting: All linter warnings addressed before PR merge
- Formatting: Auto-formatted code (no manual style debates)

**Integration with CI/CD** (Future):
- GitHub Actions workflow will run these checks
- Block PRs on failing tests or linting
- For now, document locally how to run all checks

## Dependencies

- **Blocks**: None (tooling enhances development but doesn't block other work)
- **Blocked By**:
  - EPIC-1-1 (Repository structure needed)
  - EPIC-1-2 (Development environments needed to install tools)
- **Related**:
  - EPIC-2-2 (Database models will need tests)
  - EPIC-3-1 (Vault utilities will need tests)
  - EPIC-4-2 (Config loaders will need tests)

## Verification

### Python Tooling Verification
```bash
cd api-service
source venv/bin/activate

# Verify pytest
pytest --version
pytest tests/test_sample.py -v
# Should pass (sample test created)

# Verify linting (Ruff example)
ruff check src/
# Should report style violations or "All checks passed!"

# Verify formatting
black --check src/
# Should report if files need formatting or "All done!"

# Auto-format
black src/

# Verify isort
isort --check-only src/
```

### Rust Tooling Verification
```bash
# Verify formatting
cd cli
cargo fmt -- --check
# Should report if files need formatting

# Auto-format
cargo fmt

# Verify clippy
cargo clippy -- -D warnings
# Should pass without warnings

# Verify tests run
cargo test
# Should pass all tests (including sample test)

# Same for sync-service
cd ../sync-service
cargo fmt -- --check
cargo clippy -- -D warnings
cargo test
```

### Pre-commit Hooks Verification (if implemented)
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
# Should pass all checks

# Test hook on commit (make a change and commit)
# Hooks should run automatically
```

**Completion Criteria**:
- [ ] All Python tools installed and working (pytest, linting, formatting)
- [ ] All Rust tools working (cargo test, clippy, fmt)
- [ ] Sample tests created and passing for both languages
- [ ] Development workflow documented
- [ ] A developer can run `pytest` and `cargo test` successfully
- [ ] Linting and formatting commands execute without errors
- [ ] docs/development.md provides clear instructions for running all quality checks
