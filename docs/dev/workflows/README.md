# Feature Development Workflows

This directory contains workflow skill definitions for structured feature development in Noosphere.

## Available Workflows

### [feature-development-python.workflow.md](./feature-development-python.workflow.md)

**For**: api-service (Python/FastAPI)

**Use When**: Implementing API endpoints, database models, background jobs, AI classification features

**Quality Gates**:
- 90% test coverage minimum
- ruff format + ruff check (linting)
- pyright (strict type checking)
- pytest with coverage reporting

**Tech Stack**: Python 3.14, FastAPI, SQLAlchemy, PostgreSQL, uv

**Workflow Steps**: 11 steps (includes Step 2.5 for context isolation)

---

### [feature-development-rust.workflow.md](./feature-development-rust.workflow.md)

**For**: cli (ratatui TUI) and sync-service (async daemon)

**Use When**: Implementing CLI features, keyboard handling, file watching, async operations

**Quality Gates**:
- 80% test coverage target (cargo-llvm-cov)
- cargo clippy (all warnings as errors)
- cargo fmt (automated formatting)
- cargo doc (public items documented)
- cargo check (compilation verification)

**Tech Stack**: Rust 1.70+, ratatui, tokio, notify, reqwest

**Workflow Steps**: 11 steps (includes Step 2.5 for service disambiguation)

---

## How to Use Workflows

### 1. Start with GitHub Issue

```bash
# Find your issue (assigned to you, status ready)
gh issue list --assignee "@me" --label "status/ready"

# View issue details
gh issue view EPIC-X-Y --json title,body,labels,assignees,milestone
```

### 2. Determine Service from Labels

Check the `service/` labels on the issue:
- `service/api-service` → Use **Python workflow**
- `service/cli` → Use **Rust workflow**
- `service/sync-service` → Use **Rust workflow**
- Multiple services → May need to follow both workflows

### 3. Invoke Appropriate Workflow

- For **Python/API work**: Follow `feature-development-python.workflow.md`
- For **Rust/CLI work**: Follow `feature-development-rust.workflow.md`

The workflow will guide you through all 11 steps with approval checkpoints.

### 4. Workflow Steps Overview

All workflows follow an 11-step process:

| Step | Description | Approval? |
|------|-------------|-----------|
| 1 | Pull issue & confirm understanding | ✓ Required |
| 2 | Create feature branch (git-flow) | - |
| 2.5 | **Load service context** (read AGENTS.md) | - |
| 3 | Create implementation plan | ✓ Required |
| 4 | Save & post plan to GitHub | - |
| 5 | Implement following approved plan | - |
| 6 | Run linters/formatters/type checks | ✗ Must pass |
| 7 | Write tests | - |
| 8 | Run tests with coverage | ✗ Must pass |
| 9 | Final quality check | ✗ Must pass |
| 10 | Write commit message | ✓ Required |
| 11 | Create PR & transition issue | - |

**✓ Approval Required**: Explicit user confirmation needed before proceeding

**✗ Must Pass**: Non-negotiable quality gate, workflow blocks until passing

### 5. Quality Gates (Non-Negotiable)

Each workflow has strict quality gates that must pass:

**Python (api-service)**:
```bash
cd api-service

# Step 6: Linting & Type Checking
uv run ruff format app/      # Auto-fixes formatting
uv run ruff check app/       # Linting (must pass)
uv run pyright app/          # Type checking (must pass)

# Step 8: Tests & Coverage (90% minimum)
uv run pytest -v --cov=app --cov-fail-under=90 --cov-report=term-missing
```

**Rust (cli or sync-service)**:
```bash
cd cli  # or sync-service

# Step 6: Linting & Type Checking
cargo fmt                    # Auto-fixes formatting
cargo clippy --all-targets --all-features -- -D warnings  # Must pass
cargo check --all-targets --all-features                   # Must compile

# Step 8: Tests & Coverage (80% target)
cargo llvm-cov --all-features --workspace --lcov --output-path lcov.info test
cargo llvm-cov --all-features --workspace --html  # View coverage report
```

**Workflow blocks at quality gates until all checks pass.**

### 6. Plans Directory

Implementation plans are saved to `docs/dev/plans/EPIC-X-Y-name.md` and posted as GitHub issue comments.

Plans include:
- Files to create/modify with rationale
- Architecture decisions
- Implementation steps
- Testing strategy
- Verification commands

See [../plans/README.md](../plans/README.md) for plan structure details.

## MCP Tools Integration

Both workflows leverage MCP tools for enhanced capabilities:

### sequential-thinking (Step 3: Planning)

**Purpose**: Structured problem decomposition and feature planning

**When to Use**: During implementation planning (Step 3) for complex features

**Examples**:

**Python/FastAPI**:
```
"Break down the implementation of user authentication for FastAPI/PostgreSQL backend.
Consider database schema, API endpoints, service layer, JWT tokens, and testing strategy."
```

**Rust/CLI**:
```
"Plan TUI feature for resource browsing using Elm Architecture (ratatui).
Consider: Model state, Update logic, View rendering, keyboard event handling, terminal layout."
```

**Rust/Daemon**:
```
"Plan async daemon feature for file synchronization using tokio.
Consider: File watching (notify), async task spawning, error handling, graceful shutdown."
```

### context7 (Step 5: Implementation)

**Purpose**: Fetch up-to-date library documentation and code examples

**When to Use**: Before implementing with external libraries/frameworks

**Python Examples**:
```bash
# FastAPI patterns
resolve-library-id: "fastapi"
query-docs: libraryId="/fastapi/fastapi" query="dependency injection patterns"

# SQLAlchemy async
resolve-library-id: "sqlalchemy"
query-docs: libraryId="/sqlalchemy/sqlalchemy" query="async session management"

# Pydantic v2
resolve-library-id: "pydantic"
query-docs: libraryId="/pydantic/pydantic" query="custom validators v2"
```

**Rust Examples**:
```bash
# ratatui (TUI framework)
resolve-library-id: "ratatui"
query-docs: libraryId="/ratatui/ratatui" query="event handling patterns"

# tokio (async runtime)
resolve-library-id: "tokio"
query-docs: libraryId="/tokio-rs/tokio" query="select! macro usage"

# notify (file watching)
resolve-library-id: "notify"
query-docs: libraryId="/notify-rs/notify" query="debouncer configuration"
```

**Benefits**:
- Ensures up-to-date API usage
- Avoids deprecated patterns
- Follows official best practices
- Reduces implementation errors

## Service Context Isolation

**Critical**: Always read the appropriate AGENTS.md file first (Step 2.5) to load service-specific conventions.

### Why Context Isolation Matters

Noosphere has 3 services with different languages and architectures:
- **api-service**: Python/FastAPI with `app/` layout
- **cli**: Rust with Elm Architecture (ratatui)
- **sync-service**: Rust async daemon

**Without context isolation**, you might:
- Use Python conventions in Rust code (or vice versa)
- Apply FastAPI patterns to TUI code
- Confuse daemon architecture with CLI architecture

### How to Maintain Context Isolation

**Step 2.5 of every workflow**:

1. **Read the appropriate AGENTS.md file**:
   - For Python work: Read `api-service/AGENTS.md`
   - For CLI work: Read `cli/AGENTS.md`
   - For daemon work: Read `sync-service/AGENTS.md`

2. **Load service-specific conventions**:
   - Language (Python 3.14 or Rust 1.70+)
   - Framework (FastAPI or ratatui or tokio)
   - Tooling (uv/ruff/pyright or cargo/clippy)
   - Architecture (app/ layout or Elm Architecture or async daemon)

3. **Scope all operations to service directory**:
   - Use `path="api-service/"` in Grep/Glob/Explore
   - Use `path="cli/"` in Grep/Glob/Explore
   - Use `path="sync-service/"` in Grep/Glob/Explore

4. **No cross-service pollution**:
   - Don't read files from other services unless explicitly needed for integration
   - Don't apply patterns from one service to another

**Result**: Clean, idiomatic code that follows each service's conventions.

## Git-Flow Branch Naming

Both workflows use git-flow naming conventions:

**Format**: `feature/EPIC-X-Y-brief-description`

**Examples**:
- `feature/EPIC-1-2-development-environments`
- `feature/EPIC-2-2-sqlalchemy-models`
- `feature/EPIC-3-1-vault-directory-structure`
- `feature/EPIC-5-1-health-check-endpoint`

**Branches**:
- **develop**: Integration branch (all features merge here)
- **main**: Production branch (releases only)
- **feature/**: Feature branches (created from develop)

## GitHub Automation

Both workflows include GitHub automation:

### Step 1: Issue Assignment & Status
```bash
# Auto-assign to current user
gh issue edit EPIC-X-Y --add-assignee "@me"

# Transition to in-progress (remove ready)
gh issue edit EPIC-X-Y --add-label "status/in-progress" --remove-label "status/ready"

# Link to parent epic
EPIC_NUM=$(echo "EPIC-X-Y" | grep -oE 'EPIC-[0-9]+' | head -1)
gh issue list --search "is:issue $EPIC_NUM in:title type/epic" --json number --jq '.[0].number' | \
  xargs -I {} gh issue comment {} --body "Starting work on #ISSUE_NUMBER"
```

### Step 4: Plan Posting
```bash
# Post implementation plan to issue as comment
gh issue comment EPIC-X-Y --body-file docs/dev/plans/EPIC-X-Y-brief-description.md
```

### Step 10: Commit Reference
```bash
# Add commit SHA to issue
COMMIT_SHA=$(git rev-parse HEAD)
BRANCH=$(git branch --show-current)
gh issue comment EPIC-X-Y --body "Commit: $COMMIT_SHA on branch $BRANCH"
```

### Step 11: PR Creation & Issue Transition
```bash
# Create PR with template
gh pr create --title "[EPIC-X-Y] Brief description" --body "..."

# Auto-transition to in-review (remove in-progress)
gh issue edit EPIC-X-Y --add-label "status/in-review" --remove-label "status/in-progress"

# Link PR to epic
gh issue comment EPIC_NUMBER --body "PR created for EPIC-X-Y: $(gh pr view --json url -q .url)"
```

## Coverage Thresholds

### Python: 90% Minimum

**Rationale**:
- FastAPI routes are highly testable
- Database operations with async SQLAlchemy
- Business logic in services layer
- 90% is achievable without excessive effort

**Enforcement**:
```bash
uv run pytest --cov=app --cov-fail-under=90 --cov-report=term-missing
```

### Rust: 80% Target

**Rationale**:
- Type system provides compile-time guarantees
- Pattern matching exhaustiveness is enforced
- Some unsafe/low-level code is hard to test
- Macro-generated code often excluded
- 80% is strong for production Rust code

**Enforcement**:
```bash
cargo llvm-cov --all-features --workspace --lcov --output-path lcov.info test
cargo llvm-cov --all-features --workspace --html  # View report
```

**Why lower for Rust?**
Rust's type system catches entire classes of bugs that would require tests in Python:
- Null pointer exceptions (impossible in safe Rust)
- Data races (prevented by borrow checker)
- Type errors (caught at compile time)
- Memory leaks (RAII + ownership)

## Commit Message Format

### Python (api-service)
```
[EPIC-X-Y] Component: Brief description

- What: Summary of implementation
- Why: Links to acceptance criteria
- How: Brief technical summary

Acceptance criteria addressed:
- [ ] Criterion 1
- [ ] Criterion 2

Testing:
- Unit tests added for X
- Integration tests for Y
- Coverage: XX%

Database changes:
- Migration: migrations/versions/xxx_description.py

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Rust (cli or sync-service)
```
[EPIC-X-Y] Component: Brief description

Implementation:
- Added X module/struct/trait
- Implemented Y for Z
- Updated Cargo.toml dependencies (if applicable)

Acceptance criteria addressed:
- [ ] Criterion 1
- [ ] Criterion 2

Testing:
- Unit tests: X tests
- Integration tests: Y tests
- Coverage: XX% (target: 80%+)
- All clippy warnings resolved

Cargo changes:
- Added dependency: crate-name 0.x.y
- Updated Cargo.lock (committed)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Related Documentation

- [GitHub Workflow Guide](../../github-workflow.md) - Issue/PR management, labels, milestones
- [Coding Standards](../../agents/standards.md) - Code quality requirements for Python and Rust
- [Implementation Roadmap](../../project/implementation-roadmap.md) - Development phases and epics
- [AGENTS.md Files](../../agents/) - Service-specific context and conventions
  - [api-service/AGENTS.md](../../../api-service/AGENTS.md) - Python/FastAPI context
  - [cli/AGENTS.md](../../../cli/AGENTS.md) - Rust/ratatui/Elm Architecture context
  - [sync-service/AGENTS.md](../../../sync-service/AGENTS.md) - Rust/tokio/daemon context
- [Plans Directory](../plans/README.md) - Implementation plan structure and lifecycle

## Troubleshooting

### Quality Gate Failures

**Python - ruff check fails**:
```bash
# Fix auto-fixable issues
uv run ruff check app/ --fix

# Re-run to verify
uv run ruff check app/
```

**Python - pyright fails**:
```bash
# Check specific file
uv run pyright app/api/endpoints/v1/resources.py

# Common fixes:
# - Add type annotations
# - Fix Optional[] vs None handling
# - Import missing types
```

**Rust - clippy warnings**:
```bash
# See detailed warnings
cargo clippy --all-targets --all-features

# Common fixes:
# - Use .clone() explicitly
# - Add #[allow(clippy::...)] for false positives
# - Refactor complex expressions
```

### Coverage Below Threshold

**Python (< 90%)**:
```bash
# Identify missing coverage
uv run pytest --cov=app --cov-report=term-missing

# Check HTML report
uv run pytest --cov=app --cov-report=html
open htmlcov/index.html  # View uncovered lines

# Add tests for:
# - Error cases (validation failures, not found)
# - Edge cases (empty input, large input)
# - Alternative code paths
```

**Rust (< 80%)**:
```bash
# View HTML coverage report
cargo llvm-cov --all-features --workspace --html
# Open target/llvm-cov/html/index.html

# Add tests for:
# - Result::Err paths
# - Pattern matching branches
# - Edge cases
```

### Context Mixing Issues

**Symptom**: Applied wrong conventions (Python in Rust, or vice versa)

**Fix**:
1. Stop implementation
2. Re-read appropriate AGENTS.md file (Step 2.5)
3. Review changes for convention violations
4. Refactor to match service conventions

**Prevention**:
- Always do Step 2.5 first
- Scope all operations to service directory
- Review AGENTS.md when switching services

## Best Practices

1. **Always read AGENTS.md first** (Step 2.5) - prevents convention mixing
2. **Get plan approval** (Step 3) before implementing - saves rework
3. **Use MCP tools** (sequential-thinking, Context7) - better planning and implementation
4. **Run quality checks frequently** - catch issues early
5. **Write tests as you go** - don't wait until Step 7
6. **Review coverage reports** - identify gaps before Step 8
7. **Commit Cargo.lock changes** (Rust) - ensures reproducible builds
8. **Save plans to docs/dev/plans/** - create project knowledge base
9. **Link PRs to epics** - maintain traceability
10. **Follow git-flow** - consistent branching strategy
