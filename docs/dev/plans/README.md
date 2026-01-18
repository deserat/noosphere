# Implementation Plans

This directory stores implementation plans created during feature development.

## File Naming Convention

```
EPIC-X-Y-brief-description.md
```

**Format**: EPIC number, story number, brief slug describing the feature

**Examples**:
- `EPIC-1-2-development-environments.md`
- `EPIC-2-2-sqlalchemy-models.md`
- `EPIC-3-1-vault-directory-structure.md`
- `EPIC-5-1-health-check-endpoint.md`
- `EPIC-7-3-resource-view-tui.md`

## Plan Lifecycle

### 1. Creation (Step 3 of Feature Workflow)

Generated during **Step 3: Create Implementation Plan** of the feature workflow.

**Who creates it**: Claude Code (with developer approval)

**When**: After reading issue requirements, before implementation begins

**Process**:
1. Use sequential-thinking MCP for structured planning
2. Use Explore subagent to analyze existing patterns
3. Create detailed plan with architecture decisions
4. Present to developer for approval
5. Iterate if rejected

### 2. Approval (Step 3 → Step 4 Transition)

**Developer reviews and approves** the implementation plan.

**Approval checklist**:
- [ ] Plan addresses all acceptance criteria
- [ ] Architecture decisions are sound
- [ ] Files to create/modify are correct
- [ ] Dependencies are identified
- [ ] Testing strategy is comprehensive
- [ ] Edge cases are considered

**If rejected**: Plan is revised based on feedback and re-presented.

### 3. Storage (Step 4 of Feature Workflow)

**Local storage**: Plan saved to `docs/dev/plans/EPIC-X-Y-brief-description.md`

**Why save locally**:
- Creates project knowledge base
- Enables future developers to understand decisions
- Provides context for code reviews
- Documents architectural evolution

### 4. Publishing (Step 4 of Feature Workflow)

**GitHub comment**: Plan posted to issue as comment

```bash
gh issue comment EPIC-X-Y --body-file docs/dev/plans/EPIC-X-Y-brief-description.md
```

**Why post to GitHub**:
- Links plan to issue for traceability
- Visible in issue timeline
- Reviewers can see plan before PR
- Stakeholders can understand approach

### 5. Reference (During Implementation & Review)

**During implementation** (Steps 5-9):
- Developer follows approved plan exactly
- Plan serves as implementation checklist
- Deviations require re-approval

**During code review**:
- Reviewers verify implementation matches plan
- Plan provides context for architectural decisions
- Edge cases from plan are tested

**In commit messages** (Step 10):
- Reference plan decisions
- Link to acceptance criteria from plan

**In PRs** (Step 11):
- Link to plan in PR description
- Verify all plan steps completed

## Plan Structure

Each plan should include:

### Header (Metadata)

```markdown
# EPIC-X-Y: Feature Title

## Issue Reference
- **GitHub Issue**: #ISSUE_NUMBER
- **Epic**: EPIC-X (if part of larger epic)
- **Priority**: P0/P1/P2/P3
- **Story Points**: 1-13
- **Service(s)**: api-service / cli / sync-service / multiple
```

**Purpose**: Traceability and context

### Feature Summary

```markdown
## Feature Summary
[Brief description from GitHub issue - what problem does this solve?]

User story format (if applicable):
As a [role],
I need [capability],
So that [business value].
```

**Purpose**: Ensure everyone understands the "why"

### Implementation Plan

```markdown
## Implementation Plan

### Files to Create
- `path/to/new/file.py` - Purpose and rationale
- `path/to/another/file.rs` - What it does

### Files to Modify
- `path/to/existing/file.py` - What changes and why
- `path/to/another/existing.rs` - Specific modifications

### Architecture Decisions
- **Decision 1**: Rationale and trade-offs considered
- **Decision 2**: Why this approach over alternatives
- **Decision 3**: Dependencies and implications

### API Changes (if applicable - for api-service)
- **New endpoints**:
  - `POST /api/v1/resources` - Create resource
  - `GET /api/v1/resources/{id}` - Get resource by ID
- **Modified endpoints**:
  - `GET /api/v1/users` - Added pagination support
- **Request/Response schemas**:
  - `ResourceCreate` (Pydantic model)
  - `ResourceResponse` (Pydantic model)

### Database Changes (if applicable - for api-service)
- **New tables**:
  - `resources` - Stores resource data
- **Modified columns**:
  - `users.last_login` - Added timestamp column
- **Indexes**:
  - `idx_resources_name` - For fast lookups
- **Migration strategy**:
  - Migration: `migrations/versions/xxx_add_resources.py`
  - Rollback: `alembic downgrade -1`

### UI Changes (if applicable - for cli)
- **New components**:
  - `ResourceViewWidget` - Display resources in TUI
- **Layout changes**:
  - Added panel to main layout
- **Keyboard shortcuts**:
  - `Ctrl+R` - Toggle resource view
  - `Up/Down` - Navigate list

### Async Tasks (if applicable - for sync-service)
- **New tasks**:
  - `SyncTask` - Sync files to API
- **Event handlers**:
  - File change event → trigger sync
- **Graceful shutdown**:
  - SIGTERM handling

### Dependencies
- **Blocks**: #ISSUE_NUM (must complete first)
- **Blocked by**: #ISSUE_NUM (waiting for)
- **Related**: #ISSUE_NUM (similar work)

### Cargo Changes (if applicable - for Rust services)
- **New dependencies**:
  - `notify-debouncer-full = "0.3"` - File watching with debouncing
- **Updated dependencies**:
  - `tokio = "1.35"` (from 1.34)
```

**Purpose**: Detailed roadmap for implementation

### Implementation Steps

```markdown
## Implementation Steps

1. **Create database model** (if api-service)
   - Define SQLAlchemy model in `app/models/resource.py`
   - Add relationships and constraints
   - Import in `app/db/base.py`

2. **Create Alembic migration** (if api-service)
   - `alembic revision -m "add resources table"`
   - Test upgrade and downgrade
   - Apply to local database

3. **Create Pydantic schemas** (if api-service)
   - `ResourceCreate` - Request validation
   - `ResourceResponse` - API response
   - Add to `app/schemas/resource.py`

4. **Implement service layer** (if api-service)
   - Create `app/services/resource_service.py`
   - Implement CRUD operations
   - Add business logic

5. **Create API endpoints** (if api-service)
   - Add routes in `app/api/endpoints/v1/resources.py`
   - Use dependency injection
   - Handle errors with HTTPExceptions

6. **Write tests**
   - Unit tests for service layer
   - Integration tests for API endpoints
   - Target: 90% coverage (Python) / 80% (Rust)
```

**Purpose**: Step-by-step guide, prevents missing steps

### Testing Strategy

```markdown
## Testing Strategy

### Unit Tests
- **Service layer** (Python):
  - Test resource creation logic
  - Test validation rules
  - Test error cases (duplicate, not found)
- **Core logic** (Rust):
  - Test state transitions
  - Test async task logic
  - Test error handling

### Integration Tests
- **API endpoints** (Python):
  - Test POST /api/v1/resources (happy path)
  - Test POST with invalid data (400 error)
  - Test GET with non-existent ID (404 error)
- **Full workflow** (Rust):
  - Test keyboard event handling
  - Test file watching and sync
  - Test graceful shutdown

### Coverage Target
- **Python**: 90% minimum
- **Rust**: 80% target

### Test Data
- **Fixtures**: Use pytest fixtures for database setup
- **Factories**: Use factory pattern for test objects
- **Mocks**: Mock external API calls (if needed)
```

**Purpose**: Ensure comprehensive testing, prevent gaps

### Edge Cases & Considerations

```markdown
## Edge Cases & Considerations

### Edge Case 1: Empty Input
**Problem**: What happens if user submits empty name?
**Solution**: Pydantic validation with `min_length=1`

### Edge Case 2: Duplicate Resource
**Problem**: What if resource with same name exists?
**Solution**: Database unique constraint + handle IntegrityError

### Edge Case 3: Large File Upload
**Problem**: What if file is larger than 10MB?
**Solution**: FastAPI request size limit + validation

### Edge Case 4: Terminal Resize (CLI)
**Problem**: What if terminal is resized during rendering?
**Solution**: ratatui handles automatically with Layout recalculation

### Edge Case 5: File Deleted During Sync (Daemon)
**Problem**: What if file is deleted while sync is in progress?
**Solution**: Handle NotFound error, log and continue

### Security Considerations
- **SQL Injection**: Using SQLAlchemy ORM (parameterized queries)
- **Input Validation**: Pydantic schemas validate all input
- **Authentication**: JWT token required for all endpoints
- **Authorization**: Check user owns resource before modification

### Performance Considerations
- **Database Indexes**: Add index on `name` column for fast lookups
- **Pagination**: Limit results to 100 per page
- **Caching**: Consider Redis for frequently accessed resources
- **Async**: Use async SQLAlchemy for non-blocking I/O
```

**Purpose**: Prevent bugs, ensure robustness

### Verification

```markdown
## Verification

How to verify this implementation is complete and working:

### Manual Testing

**API Service**:
```bash
# Start API server
cd api-service
uv run uvicorn app.main:app --reload

# Test create endpoint
curl -X POST http://localhost:8000/api/v1/resources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "test-resource"}'

# Expected: 201 Created with resource JSON

# Test get endpoint
curl http://localhost:8000/api/v1/resources/1 \
  -H "Authorization: Bearer <token>"

# Expected: 200 OK with resource JSON
```

**CLI**:
```bash
# Start CLI
cd cli
cargo run

# Expected: TUI displays
# Press Ctrl+R to toggle resource view
# Expected: Resource panel appears
# Use Up/Down arrows to navigate
# Expected: Selection changes
```

**Sync Service**:
```bash
# Start daemon
cd sync-service
cargo run

# In another terminal:
touch ~/noosphere/vault/test.md

# Expected: Daemon logs file change event
# Expected: API sync triggered
# Expected: Resource created via API
```

### Automated Testing

```bash
# Python tests
cd api-service
uv run pytest -v --cov=app --cov-fail-under=90

# Expected: All tests pass, coverage >= 90%

# Rust tests
cd cli  # or sync-service
cargo test --all-features --workspace
cargo llvm-cov --all-features --workspace --summary-only

# Expected: All tests pass, coverage >= 80%
```

### Database Verification

```bash
# Check migration applied
cd api-service
alembic current
# Expected: Shows current revision

# Check table created
uv run python -c "
from app.db.session import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print(inspector.get_table_names())
"
# Expected: 'resources' in table list
```
```

**Purpose**: Clear acceptance criteria, reproducible verification

## Maintenance

### Archiving Completed Plans (Optional)

After PR merges and feature is deployed:

```bash
# Optional: Archive old plans
mkdir -p docs/dev/plans/archive/phase-1/
mv docs/dev/plans/EPIC-1-*.md docs/dev/plans/archive/phase-1/
```

**Benefits**:
- Keeps plans/ directory focused on active work
- Preserves plans for historical reference
- Organizes by development phase

**Note**: Archiving is optional. Plans can remain in `docs/dev/plans/` indefinitely.

### Updating Plans

**If requirements change during implementation**:
1. Update the plan file
2. Post updated plan to GitHub issue:
   ```bash
   gh issue comment EPIC-X-Y --body "Updated implementation plan: [changes]"
   gh issue comment EPIC-X-Y --body-file docs/dev/plans/EPIC-X-Y-brief-description.md
   ```
3. Get re-approval from developer

**Do NOT**:
- Implement changes without updating plan
- Skip re-approval for significant changes

### Reviewing Old Plans

Plans serve as architectural documentation:

**When reviewing old plans**:
- Understand past architectural decisions
- Learn from previous approaches
- Identify patterns to reuse
- Avoid repeating past mistakes

**When to reference**:
- Implementing similar features
- Refactoring existing code
- Onboarding new developers
- Writing architectural documentation

## Plan Templates

### Python (api-service) Template

```markdown
# EPIC-X-Y: Feature Title

## Issue Reference
- **GitHub Issue**: #ISSUE_NUMBER
- **Epic**: EPIC-X
- **Priority**: P0/P1/P2
- **Story Points**: X
- **Service**: api-service

## Feature Summary
[Brief description]

## Implementation Plan

### Files to Create
- `api-service/app/models/resource.py` - SQLAlchemy model

### Files to Modify
- `api-service/app/db/base.py` - Import new model

### Architecture Decisions
- Using async SQLAlchemy for database operations

### API Changes
- `POST /api/v1/resources` - Create resource

### Database Changes
- New table: `resources`
- Migration: `alembic revision -m "add resources table"`

## Implementation Steps
1. Create database model
2. Create migration
3. Create schemas
4. Implement service layer
5. Create endpoints
6. Write tests

## Testing Strategy
- Unit tests for service layer
- Integration tests for API endpoints
- Coverage target: 90%+

## Edge Cases & Considerations
- Validation: Pydantic min_length=1
- Duplicates: Unique constraint

## Verification
```bash
cd api-service
uv run uvicorn app.main:app --reload
curl -X POST http://localhost:8000/api/v1/resources \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'
```
```

### Rust (CLI) Template

```markdown
# EPIC-X-Y: Feature Title (CLI)

## Issue Reference
- **GitHub Issue**: #ISSUE_NUMBER
- **Epic**: EPIC-X
- **Priority**: P0/P1/P2
- **Story Points**: X
- **Service**: cli

## Feature Summary
[Brief description]

## Implementation Plan

### Files to Create
- `cli/src/ui/components/resource_view.rs` - New TUI widget

### Files to Modify
- `cli/src/app.rs` - Add state for new feature

### Architecture Decisions
- Using Elm Architecture (Model-Update-View)

### UI Changes
- New panel in main layout
- Keyboard shortcut: Ctrl+R

### State Changes
- Add `ResourceViewMode` to `AppMode` enum

## Implementation Steps
1. Define state types
2. Create UI component
3. Add keyboard handlers
4. Update view rendering
5. Write tests

## Testing Strategy
- Unit tests for state transitions
- Integration tests for keyboard events
- Coverage target: 80%+

## Edge Cases & Considerations
- Terminal resize: ratatui handles automatically

## Verification
```bash
cd cli
cargo run
# Press Ctrl+R to toggle resource view
```
```

### Rust (sync-service) Template

```markdown
# EPIC-X-Y: Feature Title (Sync Service)

## Issue Reference
- **GitHub Issue**: #ISSUE_NUMBER
- **Epic**: EPIC-X
- **Priority**: P0/P1/P2
- **Story Points**: X
- **Service**: sync-service

## Feature Summary
[Brief description]

## Implementation Plan

### Files to Create
- `sync-service/src/tasks/sync_task.rs` - New async task

### Files to Modify
- `sync-service/src/main.rs` - Spawn new task

### Architecture Decisions
- Using tokio::spawn for async task

### Async Patterns
- Graceful shutdown with tokio::select!

## Implementation Steps
1. Create async task module
2. Add file event handlers
3. Implement graceful shutdown
4. Add logging
5. Write tests

## Testing Strategy
- Unit tests for task logic
- Integration tests with temporary files
- Coverage target: 80%+

## Edge Cases & Considerations
- File deleted during sync: Handle NotFound

## Verification
```bash
cd sync-service
cargo run
# Create test file in vault
touch ~/noosphere/vault/test.md
```
```

## Best Practices

1. **Write plans before coding** - Step 3 of workflow (mandatory)
2. **Get approval before implementing** - Prevents wasted effort
3. **Keep plans detailed** - Future developers will thank you
4. **Update plans if requirements change** - Keep documentation accurate
5. **Post plans to GitHub** - Create traceability
6. **Reference plans in PRs** - Provide review context
7. **Learn from old plans** - Build institutional knowledge
8. **Use templates** - Ensures consistency
9. **Consider edge cases** - Prevents bugs
10. **Include verification steps** - Makes testing reproducible

## Related Documentation

- [Workflows README](../workflows/README.md) - Feature development workflows that create these plans
- [GitHub Workflow Guide](../../github-workflow.md) - How to link plans to issues and PRs
- [Coding Standards](../../agents/standards.md) - Code quality requirements
- [AGENTS.md Files](../../agents/) - Service-specific conventions
