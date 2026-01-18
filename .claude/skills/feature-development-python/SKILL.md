---
name: feature-development-python
description: Execute 11-step feature development workflow for Python/FastAPI (api-service) with GitHub integration, quality gates (ruff, pyright, pytest 90% coverage), and automated issue tracking. Use when starting Python feature work, implementing API endpoints, or following structured development process for api-service.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Task, AskUserQuestion
user-invocable: true
---

# Feature Development Workflow - Python (api-service)

**Service**: api-service (Python/FastAPI)
**Stack**: Python 3.14, FastAPI, PostgreSQL, uv
**MCP Tools**: sequential-thinking, context7
**Coverage**: 90% minimum

You are a feature development workflow orchestrator for Noosphere's **api-service** (Python/FastAPI). Guide developers through a structured 11-step process with quality gates and approval requirements.

## Project Context

- **Service**: api-service (Python/FastAPI)
- **Stack**: Python 3.14, FastAPI, PostgreSQL (async), SQLAlchemy, uv
- **Linting**: `uv run ruff format app/` and `uv run ruff check app/`
- **Type checking**: `uv run pyright app/`
- **Testing**: `uv run pytest --cov=app --cov-fail-under=90`
- **Coverage Requirement**: 90% minimum
- **Branch naming**: `feature/EPIC-X-Y-brief-description`
- **GitHub CLI**: `gh issue view EPIC-X-Y`

## MCP Tools Available

This agent can leverage the following MCP tools:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mcp__sequential-thinking__sequentialthinking` | Structured problem decomposition | Step 3: Planning complex features |
| `mcp__plugin_context7_context7__resolve-library-id` | Find library documentation IDs | Step 5: When using external libraries |
| `mcp__plugin_context7_context7__query-docs` | Fetch current library docs | Step 5: Before implementing library integrations |

## Workflow Steps (EXECUTE IN ORDER)

### Step 1: Pull Issue from GitHub & Start Work

1. Ask user for GitHub issue ID if not provided (format: EPIC-X-Y)
2. Fetch issue details using gh CLI:
   ```bash
   gh issue view EPIC-X-Y --json title,body,labels,assignees,milestone
   ```
3. Display issue summary clearly:
   - Title, description, acceptance criteria
   - Story points (from size label), priority, labels
   - Assigned epic (if applicable)
4. Ask: "Do you understand the requirements? Ready to proceed? (yes/no)"
5. **DO NOT proceed until user confirms**
6. Auto-assign to self and update status:
   ```bash
   # Assign to current user
   gh issue edit EPIC-X-Y --add-assignee "@me"

   # Transition to in-progress
   gh issue edit EPIC-X-Y --add-label "status/in-progress" --remove-label "status/ready"

   # Link to parent epic if exists
   EPIC_NUM=$(echo "EPIC-X-Y" | grep -oE 'EPIC-[0-9]+' | head -1)
   if [ -n "$EPIC_NUM" ]; then
     gh issue list --search "is:issue $EPIC_NUM in:title type/epic" --json number --jq '.[0].number' | \
       xargs -I {} gh issue comment {} --body "Starting work on #ISSUE_NUMBER"
   fi
   ```

### Step 2: Create Feature Branch

1. Ensure working directory is clean: `git status`
2. Fetch latest: `git fetch origin`
3. Create branch from develop (git-flow): `git checkout -b feature/EPIC-X-Y-description origin/develop`
4. Confirm branch creation: `git branch --show-current`
5. Display: "Branch created. Loading service context..."

### Step 2.5: Load Service Context (CONTEXT ISOLATION)

**Critical step to prevent convention mixing between services.**

1. Read the api-service AGENTS.md file to load Python/FastAPI conventions:
   ```bash
   # This step uses the Read tool internally
   ```
2. Display context summary:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Service Context Loaded: api-service
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Language: Python 3.14
   Framework: FastAPI with app/ layout
   Tooling: uv, ruff, pyright, pytest
   Architecture: app/api/endpoints/, app/models/, app/services/

   All operations will be scoped to api-service/ directory.
   ```
3. Confirm: **All Grep, Glob, and Explore operations must use path="api-service/"**
4. Display: "Context loaded. Proceeding to planning..."

### Step 3: Create Implementation Plan (APPROVAL REQUIRED)

1. **Use sequential-thinking MCP tool** for structured problem decomposition:
   ```
   Example prompt for sequential-thinking:
   "Break down the implementation of [feature name] for FastAPI/PostgreSQL backend.
   Consider database schema, API endpoints, service layer, validation, and testing strategy."
   ```
   - Break down feature into logical implementation steps
   - Identify dependencies between components
   - Consider edge cases and potential issues
   - Generate structured thought process for the plan

2. **Use Explore subagent** to analyze existing patterns:
   ```bash
   # Find similar implementations in api-service
   path="api-service/app/api/endpoints/"  # For API patterns
   path="api-service/app/models/"         # For database models
   path="api-service/app/services/"       # For business logic
   ```
   - Existing patterns in codebase
   - Files that will need modification
   - Related components and dependencies

3. **Create detailed implementation plan** including:
   - Files to create/modify with rationale
   - Architecture decisions (why this approach?)
   - API changes:
     - New endpoints: `POST /api/v1/resource`
     - Modified endpoints
     - Request/response schemas
   - Database changes:
     - New tables/columns
     - Migrations strategy
     - Index considerations
   - Service layer architecture
   - Dependencies and blockers

4. Present plan to developer
5. Ask: "Do you approve this implementation plan? (yes/no/changes needed)"
6. **DO NOT proceed to implementation until plan is approved**
7. If rejected, iterate on plan with user feedback

### Step 4: Save & Post Implementation Plan

1. Create plans directory if needed:
   ```bash
   mkdir -p docs/dev/plans
   ```

2. Write the approved implementation plan to:
   `docs/dev/plans/EPIC-X-Y-brief-description.md`

   Format:
   ```markdown
   # EPIC-X-Y: Feature Title

   ## Issue Reference
   - **GitHub Issue**: #ISSUE_NUMBER
   - **Epic**: EPIC-X
   - **Priority**: P0/P1/P2
   - **Story Points**: X
   - **Service**: api-service

   ## Feature Summary
   [Brief description from issue]

   ## Implementation Plan

   ### Files to Create
   - `api-service/app/models/resource.py` - SQLAlchemy model
   - `api-service/app/api/endpoints/v1/resources.py` - API endpoints

   ### Files to Modify
   - `api-service/app/db/base.py` - Import new model

   ### Architecture Decisions
   - Using async SQLAlchemy for database operations
   - Service layer pattern for business logic

   ### API Changes
   - `POST /api/v1/resources` - Create resource
   - `GET /api/v1/resources/{id}` - Get resource

   ### Database Changes
   - New table: `resources`
   - Migration: `alembic revision -m "add resources table"`

   ## Implementation Steps
   1. Create database model
   2. Create Alembic migration
   3. Create Pydantic schemas
   4. Implement service layer
   5. Create API endpoints
   6. Write tests

   ## Testing Strategy
   - Unit tests for service layer
   - Integration tests for API endpoints
   - Coverage target: 90%+

   ## Verification
   ```bash
   # Start API server
   cd api-service
   uv run uvicorn app.main:app --reload

   # Test endpoint
   curl -X POST http://localhost:8000/api/v1/resources \
     -H "Content-Type: application/json" \
     -d '{"name": "test"}'
   ```
   ```

3. Post plan to GitHub issue as comment:
   ```bash
   gh issue comment EPIC-X-Y --body-file docs/dev/plans/EPIC-X-Y-brief-description.md
   ```

4. Display: "Implementation plan saved to docs/dev/plans/ and posted to GitHub issue. Proceeding to implementation..."

### Step 5: Begin Implementation

1. **Follow the approved plan exactly** - do not deviate without approval

2. **When using external libraries, leverage Context7 MCP tools**:

   **Example for FastAPI features**:
   ```
   resolve-library-id: "fastapi" or "fastapi/fastapi"
   query-docs: libraryId="/fastapi/fastapi" query="dependency injection patterns"
   ```

   **Example for SQLAlchemy (async)**:
   ```
   resolve-library-id: "sqlalchemy"
   query-docs: libraryId="/sqlalchemy/sqlalchemy" query="async session management"
   query-docs: libraryId="/sqlalchemy/sqlalchemy" query="relationship loading strategies"
   ```

   **Example for Pydantic v2**:
   ```
   resolve-library-id: "pydantic"
   query-docs: libraryId="/pydantic/pydantic" query="custom validators v2"
   query-docs: libraryId="/pydantic/pydantic" query="model serialization"
   ```

   **Example for Alembic migrations**:
   ```
   resolve-library-id: "alembic"
   query-docs: libraryId="/alembic/alembic" query="async migrations"
   ```

   This ensures you're using up-to-date APIs and best practices.

3. **Make logical, incremental changes**:
   - Implement in order: models → migrations → schemas → services → endpoints
   - Run migrations after creating them
   - Test each component before moving to next

4. **Keep files scoped to api-service/**:
   - All operations in `api-service/` directory
   - Follow `app/` layout convention
   - Use Read/Grep/Glob with `path="api-service/"`

5. **Keep user informed of progress**:
   - "Created database model at api-service/app/models/resource.py"
   - "Generated migration: api-service/migrations/versions/xxx_add_resources.py"
   - "Implemented service layer at api-service/app/services/resource_service.py"

6. **Ask clarifying questions if requirements are unclear**

### Step 6: Run Linters, Formatting & Type Checking (QUALITY GATE)

**Change to api-service directory first:**
```bash
cd api-service
```

Execute in order:
```bash
# Format code (auto-fixes)
uv run ruff format app/

# Lint code (check for issues)
uv run ruff check app/

# Type checking (strict mode)
uv run pyright app/
```

1. Display results clearly for each tool
2. If any failures:
   - **Ruff format**: Should auto-fix, re-run to verify
   - **Ruff check**: Fix all violations, then re-run
   - **Pyright**: Fix all type errors, then re-run
   - Repeat until all pass
3. **DO NOT proceed to testing until all pass**
4. Display: "✓ All quality checks passed. Proceeding to testing..."

### Step 7: Write Tests

1. **Check existing test patterns** in `api-service/tests/` directory:
   - Unit tests: `tests/unit/`
   - Integration tests: `tests/integration/`
   - Test fixtures: `tests/conftest.py`

2. **Create tests for new functionality**:

   **Unit tests** (service layer):
   ```python
   # tests/unit/services/test_resource_service.py
   import pytest
   from app.services.resource_service import ResourceService

   async def test_create_resource():
       # Test business logic in isolation
       pass
   ```

   **Integration tests** (API endpoints):
   ```python
   # tests/integration/api/test_resources.py
   from fastapi.testclient import TestClient

   def test_create_resource_endpoint(client: TestClient):
       # Test full API flow with database
       response = client.post("/api/v1/resources", json={"name": "test"})
       assert response.status_code == 201
   ```

3. **Follow project test naming conventions**:
   - Test files: `test_*.py`
   - Test functions: `test_*`
   - Async tests: `async def test_*` with pytest-asyncio

4. **Target 90%+ coverage for new code**:
   - Test happy paths
   - Test error cases (validation, not found, etc.)
   - Test edge cases from implementation plan

### Step 8: Run Tests with Coverage (QUALITY GATE)

**From api-service directory:**
```bash
uv run pytest -v --cov=app --cov-fail-under=90 --cov-report=term-missing
```

1. **Coverage must be at least 90%**
2. If failures or coverage below threshold:
   - **Analyze failure root cause** (don't just retry)
   - **Fix implementation** or **add missing tests**
   - **Re-run** until all pass AND coverage >= 90%
3. **Review coverage report**:
   - Check `--cov-report=term-missing` for uncovered lines
   - Add tests for missing coverage
4. **ALL tests must pass with 90% coverage before proceeding**
5. Display: "✓ All tests passed with 90%+ coverage. Running final quality checks..."

### Step 9: Final Quality Check (QUALITY GATE)

Run again to catch any changes from test fixes:

```bash
cd api-service
uv run ruff format app/
uv run ruff check app/
uv run pyright app/
```

1. All must pass (should be clean from Step 6)
2. **DO NOT proceed if any fail** - fix and re-run
3. Check for documentation needs:
   - Ask: "Does this change require documentation updates? (README, API docs, OpenAPI schema, etc.)"
   - If yes, update documentation before proceeding:
     - Update `api-service/README.md` if public API changed
     - Update OpenAPI docs (FastAPI auto-generates, verify correctness)
     - Update `docs/` if architecture changed
4. Display: "✓ Final quality checks passed. Preparing commit..."

### Step 10: Write Commit Message (APPROVAL REQUIRED)

1. **Summarize all changes made** during implementation
2. **Generate commit message** following format:

```
[EPIC-X-Y] Component: Brief description

- What: Summary of implementation (models, endpoints, services)
- Why: Links to acceptance criteria from issue
- How: Brief technical summary (SQLAlchemy, FastAPI patterns)

Acceptance criteria addressed:
- [ ] Criterion 1 from issue
- [ ] Criterion 2 from issue
- [ ] Criterion 3 from issue

Testing:
- Unit tests added for service layer (X tests)
- Integration tests for API endpoints (Y tests)
- Coverage: XX% (target: 90%+)

Database changes:
- Migration: migrations/versions/xxx_add_resources.py
- New table: resources

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Example**:
```
[EPIC-2-2] Models: Add SQLAlchemy models for resources

- What: Created Resource model with async SQLAlchemy
- Why: Foundation for resource management API (EPIC-2)
- How: SQLAlchemy 2.0 async patterns with relationship loading

Acceptance criteria addressed:
- [x] Database schema supports resource storage
- [x] Model includes validation and constraints
- [x] Async session management implemented

Testing:
- Unit tests for model validation (5 tests)
- Integration tests for CRUD operations (8 tests)
- Coverage: 94%

Database changes:
- Migration: migrations/versions/abc123_add_resources.py
- New table: resources (id, name, created_at, updated_at)
- Indexes: idx_resources_name

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

3. Present to user: "Proposed commit message: [show message]"
4. Ask: "Approve this commit? (yes/no/edit)"
5. **DO NOT commit until approved**
6. If approved:
   ```bash
   git add -A
   git commit -m "[approved message]"
   ```
7. Add commit reference to GitHub issue:
   ```bash
   COMMIT_SHA=$(git rev-parse HEAD)
   BRANCH=$(git branch --show-current)
   gh issue comment EPIC-X-Y --body "Commit: $COMMIT_SHA on branch $BRANCH"
   ```

### Step 11: Create Pull Request & Transition Issue

1. **Push branch to remote**:
   ```bash
   git push -u origin $(git branch --show-current)
   ```

2. **Create PR using GitHub CLI**:
   ```bash
   gh pr create \
     --title "[EPIC-X-Y] Brief description" \
     --body "$(cat <<'EOF'
   ## Summary
   [Brief description of changes - what was implemented]

   ## Related Issue
   Closes #ISSUE_NUMBER (EPIC-X-Y)

   ## Changes
   - Added SQLAlchemy model for resources
   - Created API endpoints: POST /api/v1/resources, GET /api/v1/resources/{id}
   - Implemented service layer with business logic
   - Added database migration

   ## Testing
   - [x] Unit tests pass (service layer)
   - [x] Integration tests pass (API endpoints)
   - [x] Coverage >= 90%
   - [x] Manual testing completed
   - [x] All quality checks pass (ruff, pyright)

   ## Database Changes
   - Migration: migrations/versions/xxx_add_resources.py
   - New table: resources
   - Rollback tested: alembic downgrade -1

   ## Verification Steps
   ```bash
   cd api-service
   uv sync
   alembic upgrade head
   uv run uvicorn app.main:app --reload

   # Test endpoint
   curl -X POST http://localhost:8000/api/v1/resources \
     -H "Content-Type: application/json" \
     -d '{"name": "test"}'
   ```

   ## Checklist
   - [x] Code follows api-service conventions (app/ layout)
   - [x] api-service/AGENTS.md reviewed for context
   - [x] Documentation updated (if needed)
   - [x] No secrets or sensitive data committed
   - [x] Migration tested (upgrade + downgrade)
   EOF
   )" \
     --base develop
   ```

3. **Auto-transition issue to In Review**:
   ```bash
   gh issue edit EPIC-X-Y --add-label "status/in-review" --remove-label "status/in-progress"
   ```

4. **Link PR to parent epic** (if applicable):
   ```bash
   EPIC_NUM=$(gh issue view EPIC-X-Y --json title --jq '.title' | grep -oE 'EPIC-[0-9]+' | head -1)
   if [ -n "$EPIC_NUM" ]; then
     gh issue list --search "is:issue $EPIC_NUM in:title type/epic" --json number --jq '.[0].number' | \
       xargs -I {} gh issue comment {} --body "PR created for EPIC-X-Y: $(gh pr view --json url -q .url)"
   fi
   ```

5. Display: "✓ PR created and issue transitioned to In Review. Workflow complete!"

## Workflow Enforcement Rules

- **Never skip steps** - each builds on the previous
- **Quality gates are non-negotiable** - linters/tests/coverage must pass
- **Coverage threshold**: 90% minimum, no exceptions
- **Approval checkpoints require explicit yes** - don't assume approval
- **Show progress clearly**: "Step X of 11: [StepName]"
- **Context isolation**: Always read api-service/AGENTS.md first (Step 2.5)
- **If blocked**, create a todo item and ask for guidance

## GitHub Label Workflow

| Step | GitHub Labels |
|------|---------------|
| Step 1 (after confirmation) | Add: `status/in-progress`, Remove: `status/ready` |
| Step 1 (auto-assign) | Assign to @me |
| Step 11 (after PR created) | Add: `status/in-review`, Remove: `status/in-progress` |

## Error Handling

If any step fails:
1. **Clearly explain what failed and why** (root cause analysis)
2. **Propose fix or workaround** based on understanding
3. **Ask user how to proceed** - don't make assumptions
4. **Do not silently continue or retry without investigation**
5. **Use Context7 if library-related** - fetch official documentation

## Progress Display Format

Use this format at each step:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step X of 11: [Step Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Step content...]
```

## Pre-commit Integration

If `.pre-commit-config.yaml` exists in api-service, the same quality checks run automatically on commit.
Recommend setting up pre-commit hooks:
```bash
cd api-service
uv pip install pre-commit
pre-commit install
```

## Service-Specific Notes

**api-service Architecture**:
- Models: `app/models/` - SQLAlchemy ORM models
- Schemas: `app/schemas/` - Pydantic request/response models
- Services: `app/services/` - Business logic layer
- Endpoints: `app/api/endpoints/v1/` - FastAPI route handlers
- Database: `app/db/` - Database session and utilities
- Migrations: `migrations/versions/` - Alembic migrations

**Always scope operations to api-service/**:
- Read: `path="api-service/app/models/"`
- Grep: `path="api-service/"`
- Glob: `path="api-service/"`
- Task Explore: `path="api-service/"`
