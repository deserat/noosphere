# Implementation Plan

## Development Timeline

**Target:** 5 weeks (1 month) for MVP

## Phase 1: Foundation (Week 1)

### 1.1 Project Setup
- [ ] Create directory structure for all services (cli/, api-service/, sync-service/, docs/)
- [ ] Initialize git repository
- [ ] Set up .gitignore (Python __pycache__, Rust target/, .env, etc.)
- [ ] Create Python virtual environment for api-service
- [ ] Initialize Rust projects with Cargo (CLI and sync-service)

### 1.2 Database Setup
- [ ] Install PostgreSQL 14+ locally
- [ ] Install pgvector extension
- [ ] Create SQLAlchemy models for core tables:
  - `items`
  - `users`
  - `user_config`
- [ ] Initial Alembic migration
- [ ] Database connection module
- [ ] Seed script for test data

### 1.3 File Vault
- [ ] Create `~/noosphere-vault` directory
- [ ] Create category folders (Inbox, People, Projects, Ideas, Admin)
- [ ] Markdown template with frontmatter
- [ ] Helper functions for file operations
- [ ] Lock file implementation

### 1.4 Configuration System
- [ ] YAML config file structure (`config/default.yaml`)
- [ ] Environment variable override logic
- [ ] Shared config loader module
- [ ] Document all config options

**Deliverable:** Empty vault, working database, basic project structure

## Phase 2: Core Capture & Classification (Week 2)

### 2.1 API Service - Capture Endpoint
- [ ] FastAPI app setup
- [ ] `POST /api/capture` endpoint
- [ ] File creation with lock mechanism
- [ ] UUID generation for items
- [ ] Filename sanitization and generation
- [ ] Unit tests for file operations

### 2.2 API Service - Sync Endpoint
- [ ] `POST /api/sync/file-changed` endpoint
- [ ] Accept raw file contents from sync-service
- [ ] Parse frontmatter and content
- [ ] Update item in DB
- [ ] Compute and verify content_hash
- [ ] Basic conflict detection (timestamp comparison)

### 2.3 AI Integration - Classification
- [ ] LiteLLM setup and configuration
- [ ] Classification prompt (store in DB)
- [ ] Category/subcategory/tag extraction
- [ ] Confidence scoring
- [ ] Structured JSON output parsing
- [ ] Token usage logging
- [ ] Error handling and retries
- [ ] Unit tests for classification

### 2.4 Sync Service - File Watching (Rust)
- [ ] notify crate integration for file watching
- [ ] Detect file changes (create, modify, delete, move)
- [ ] Read raw file contents
- [ ] Compute content_hash (SHA-256)
- [ ] Call POST /api/sync/file-changed with raw contents (reqwest)
- [ ] Error handling and retry logic
- [ ] Unit tests for file watching and HTTP client

### 2.5 CLI - Basic Capture
- [ ] Rust REPL loop setup
- [ ] HTTP client for API calls
- [ ] Simple capture command
- [ ] Display AI classification results
- [ ] Confirmation flow
- [ ] Error display

**Deliverable:** Can capture items via CLI, AI classifies them, saved as markdown files, synced to database

## Phase 3: Triage Mode (Week 2-3)

### 3.1 API Endpoints
- [ ] `GET /api/triage` - retrieve uncategorized items
- [ ] `POST /api/triage/approve` - bulk approve classifications
- [ ] `POST /api/triage/modify` - modify single item classification
- [ ] Response formatting with AI suggestions

### 3.2 CLI - TUI Triage Panel
- [ ] ratatui/cursive setup
- [ ] Checkbox list component
- [ ] Display AI suggestions with confidence
- [ ] Navigation (up/down, space to toggle, enter to proceed)
- [ ] Bulk approval action
- [ ] Conversational fallback for modifications
- [ ] Mode transition (TUI → REPL for conversation)

### 3.3 File Operations
- [ ] Move file from Inbox to category folder
- [ ] Update frontmatter metadata (category, subcategory, tags, state)
- [ ] Create subcategory folders on-demand
- [ ] Handle filename conflicts (append number)
- [ ] Update database after move

**Deliverable:** Interactive triage mode, can categorize multiple items quickly

## Phase 4: Review & Surfacing (Week 3)

### 4.1 Surfacing Logic
- [ ] Calculate `next_surface` dates
- [ ] Implement cascading cadence rules:
  - Base (next day)
  - General user preference
  - Category-specific rules
  - Item-specific overrides
- [ ] Surfacing query (items due/resurfacing today)
- [ ] Update `next_surface` after defer/complete actions

### 4.2 Scheduler Service
- [ ] Simple polling loop (60-second interval)
- [ ] Morning digest generation:
  - Query surfacing items
  - Format digest message
  - Write to notifications table (or trigger CLI notification)
- [ ] Surfacing date updates (periodic scan)

### 4.3 API Endpoints
- [ ] `GET /api/review` - get items for review
- [ ] `POST /api/items/{id}/defer` - defer item
- [ ] `POST /api/items/{id}/complete` - complete/archive item
- [ ] State transitions (not-started → in-progress → completed)

### 4.4 CLI - TUI Review Panel
- [ ] Review mode TUI layout (due today + resurfacing)
- [ ] Item list with states and summaries
- [ ] Navigation and selection
- [ ] Actions: defer, complete, work on
- [ ] Batch operations (defer all checked)
- [ ] Transition to editing mode

**Deliverable:** Morning digest, review workflow, items resurface based on cadence

## Phase 5: Work/Editing Mode (Week 4)

### 5.1 WebSocket Setup
- [ ] `WS /api/work/{item_id}` endpoint
- [ ] WebSocket message protocol
- [ ] Streaming conversation support
- [ ] Connection management (reconnect, timeout)

### 5.2 Conversation Engine
- [ ] LiteLLM streaming integration
- [ ] Conversation context management
- [ ] Load previous conversation history from DB
- [ ] Summarization for old conversations (RRD-style)
- [ ] Save conversation on exit
- [ ] Clarifying question detection

### 5.3 CLI - Split-Panel TUI
- [ ] Split-panel layout (left: chat, right: document)
- [ ] Markdown rendering in right panel
- [ ] Diff highlighting (additions, deletions)
- [ ] Approval flow (y/n prompt)
- [ ] Real-time updates
- [ ] Auto-detect completion ("done" keyword or agent prompt)

### 5.4 File Editing
- [ ] Apply changes to markdown content
- [ ] Lock file acquisition
- [ ] Immediate save on approval
- [ ] Update frontmatter (last_worked, state)
- [ ] Trigger sync to database
- [ ] Return to review mode (if came from there)

**Deliverable:** Conversational editing works, changes reflected in files immediately

## Phase 6: Semantic Features (Week 4-5)

### 6.1 Embeddings
- [ ] Embedding generation function (via LiteLLM)
- [ ] Async job queue for embedding updates
- [ ] Generate on item create/modify
- [ ] Store in pgvector column
- [ ] Update `embedding_updated` timestamp

### 6.2 Semantic Search
- [ ] Vector similarity queries (pgvector)
- [ ] `GET /api/search` endpoint
- [ ] Combined semantic + full-text search
- [ ] Relevance scoring
- [ ] CLI search command

### 6.3 Related Section Generation
- [ ] Detect semantically similar items
- [ ] Generate "why related" explanations
- [ ] Update markdown Related section
- [ ] Store in `item_links` table (link_type='semantic')
- [ ] Periodic regeneration task

### 6.4 Tag Suggestions
- [ ] Analyze existing tags via embeddings
- [ ] Suggest tags when creating items
- [ ] Tag promotion monitoring:
  - Detect frequently used tags
  - Identify semantic clusters
  - Suggest subcategory creation
- [ ] User approval flow for promotions

**Deliverable:** Semantic search works, Related sections auto-generated, tag suggestions appear

## Phase 7: Polish & Testing (Week 5)

### 7.1 Error Handling
- [ ] Sentry integration (all services)
- [ ] Graceful degradation:
  - AI unavailable → manual categorization
  - Database down → read-only file mode
  - Sync failures → retry with backoff
- [ ] User-friendly error messages
- [ ] Validation for user inputs
- [ ] Confirmation prompts for destructive actions

### 7.2 Testing
- [ ] Unit tests for core functions:
  - Classification logic
  - File operations
  - Sync logic
  - Surfacing calculations
- [ ] Integration tests for workflows:
  - Capture → triage → categorize
  - Review → defer/complete
  - Editing flow
- [ ] End-to-end CLI testing
- [ ] Coverage reporting

### 7.3 Documentation
- [ ] Setup guide (README.md)
- [ ] User manual (how to use each mode)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Configuration reference
- [ ] Troubleshooting guide
- [ ] Contributing guidelines

### 7.4 Performance Optimization
- [ ] Database indexes (verify all needed)
- [ ] Query optimization (EXPLAIN ANALYZE)
- [ ] Async operations where beneficial
- [ ] Caching strategies (if needed)
- [ ] Load testing (simulate heavy usage)

**Deliverable:** Stable, tested, documented MVP

## Validation & Acceptance Criteria

### MVP is complete when all criteria pass:

#### 1. Capture Workflow ✅
**Criteria:**
- Can capture 30 items in one day via CLI without friction
- Each capture takes < 5 seconds (including AI classification)
- AI correctly categorizes 90%+ of items (confidence >= 0.6)
- Malformed input handled gracefully (doesn't crash)

**Test:**
```bash
# Rapid-fire capture test
> I need to call the dentist
> Follow up with Sarah about website
> Blog post idea about productivity
> Buy groceries
> Meeting notes from standup
... (30 items)

# Verify all saved correctly
SELECT count(*) FROM items WHERE created > NOW() - INTERVAL '1 day';
-- Should be 30

# Check accuracy
SELECT count(*) FROM items WHERE confidence >= 0.9;
-- Should be >= 27 (90%)
```

#### 2. Triage Workflow ✅
**Criteria:**
- Can review and categorize all 30 items in under 10 minutes
- TUI panel with checkboxes is functional and responsive
- Bulk approval works (10+ items at once)
- Conversational modification works for edge cases
- Items move to correct folders, frontmatter updated

**Test:**
```bash
> /triage
[TUI panel appears with 30 items]
[Check 25 items, approve in bulk - takes < 2 minutes]
[5 items need conversation - takes < 8 minutes]
> done
[Exit triage]

# Verify categorization
ls ~/noosphere-vault/Inbox/  # Should be empty
ls ~/noosphere-vault/Ideas/  # Should have items
```

#### 3. Review Workflow ✅
**Criteria:**
- Morning digest surfaces at configured time (7am default)
- Items resurface according to cadence rules
- Can defer items (tomorrow or user cadence)
- Can complete/archive items
- Transition to editing mode works

**Test:**
```bash
# Configure digest for testing
# Set digest_time to 1 minute from now
# Wait for digest...

> /review
[TUI panel shows items due + resurfacing]
[Select item, press Enter]
[Editing mode opens]
> done
[Returns to review mode]
[Defer 5 items, complete 3 items]
> q

# Verify state changes
SELECT state, count(*) FROM items GROUP BY state;
-- Should show completed, deferred states
```

#### 4. Editing Workflow ✅
**Criteria:**
- Can develop blog post from idea to draft using conversational agent
- Split-panel TUI shows live diffs
- Changes saved immediately on approval
- Conversation history preserved (checked in DB)
- Ambiguous instructions prompt clarifying questions

**Test:**
```bash
> work on blog post about second brain
[Editing mode opens]
> expand the introduction
[Agent asks: "Which paragraph is the introduction?"]
> the first one
[Agent shows diff with additions]
Apply? (y/n)
> y
✓ Saved

> add a section about emergent taxonomy
[Agent generates new section, shows diff]
> y
✓ Saved

> done
[Returns to general conversation]

# Verify changes persisted
cat ~/noosphere-vault/Ideas/Creative/blog-post-second-brain.md
# Should show expanded intro + new section

# Check conversation saved
SELECT count(*) FROM conversations WHERE item_id = '...';
-- Should be 1
```

#### 5. Sync Works Reliably ✅
**Criteria:**
- Can edit same item in CLI and Obsidian without data loss
- Conflicts detected and flagged for resolution
- Lock files prevent corruption
- External file moves handled (via item ID)
- Sync is fast (< 1 second to detect and update)

**Test:**
```bash
# Test 1: Sequential edits (no conflict)
# Edit in CLI
> work on blog post
> add paragraph
> y
> done

# Edit in Obsidian
# Add a different paragraph, save

# Verify both changes present in file and DB
cat ~/noosphere-vault/Ideas/Creative/blog-post.md
# Should have both paragraphs

SELECT content_hash FROM items WHERE title LIKE '%blog%';
# Hash should match file

# Test 2: Concurrent edits (conflict)
# Edit file in Obsidian, don't save yet
# Edit in CLI
> work on blog post
> add paragraph
> y
[CLI writes file]

# Now save in Obsidian (conflict!)

# Verify conflict detected
ls ~/noosphere-vault/Ideas/Creative/
# Should see: blog-post.conflicted.md, blog-post.conflict-db.md

SELECT count(*) FROM items WHERE category='Inbox' AND title LIKE 'Conflict:%';
-- Should be 1
```

#### 6. Emergent Taxonomy Works ✅
**Criteria:**
- System suggests new subcategory based on emerging patterns
- Tag promotion mechanism functional (detects clusters)
- User can approve/reject suggestions
- Approved subcategory created, items moved

**Test:**
```bash
# Create 12 items tagged #meditation
> Capture these items: meditation technique 1, meditation practice, mindfulness exercise, ...
[Repeat 12 times with #meditation tag]

# Wait for periodic task or manually trigger
# (In production: run scheduler task)

# Check for suggestion
> /review
[Should show: "💡 Suggestion: Create subcategory Ideas/Mindfulness for 12 #meditation items?"]
> approve

# Verify subcategory created
ls ~/noosphere-vault/Ideas/Mindfulness/
# Should have 12 files

SELECT count(*) FROM items WHERE subcategory = 'Mindfulness';
-- Should be 12
```

## Next Steps After MVP

### Phase 8: Additional Surfaces (Week 6+)
- Gnome applet
- Slack bot
- Web interface
- Mobile app

### Phase 9: Advanced Features (Week 7+)
- Planning mode (project breakdown)
- Advanced search (filters, saved searches)
- Export/import (Notion, Obsidian, Roam)
- Collaboration (shared vaults)
- Scheduled surfacing (progressive throughout day)

### Phase 10: Cloud Migration (Week 8+)
- Deploy to GCP Cloud Run
- Cloud SQL + pgvector
- Authentication (Firebase)
- Multi-tenancy (data isolation)
- Billing integration

## Development Best Practices

### Code Quality
- Type hints in Python (mypy)
- Linting (ruff for Python, clippy for Rust)
- Formatting (black for Python, rustfmt for Rust)
- Pre-commit hooks (lint, test, format)

### Git Workflow
- Feature branches (`feature/capture-api`)
- Descriptive commits
- PR reviews (even for solo, use checklist)
- Tag releases (`v0.1.0-alpha`)

### Testing Strategy
- TDD where possible (write test first)
- Minimum 80% coverage for core logic
- Integration tests for workflows
- Manual testing checklist for each phase

### Documentation
- Inline comments for complex logic
- Docstrings for public APIs
- README with setup instructions
- Changelog for each release

## Risk Management

### Technical Risks
| Risk | Mitigation |
|------|------------|
| LiteLLM API changes | Pin version, monitor changelog |
| pgvector performance at scale | Benchmark early, optimize indexes |
| File sync race conditions | Thorough lock testing, stress tests |
| TUI complexity (Rust) | Start simple, iterate, consider alternatives |

### Schedule Risks
| Risk | Mitigation |
|------|------------|
| Underestimated Phase 5 (editing) | Allocate extra time, simplify UX if needed |
| Learning curve (Rust TUI) | Prototype early, have fallback (simpler CLI) |
| Scope creep | Strict MVP definition, defer nice-to-haves |

### Quality Risks
| Risk | Mitigation |
|------|------------|
| Insufficient testing | Allocate full week for Phase 7 |
| Poor UX | User testing (even with yourself), iterate |
| Performance issues | Profile early, optimize hot paths |

## Success Metrics

### Daily Usage (Personal)
- Capture 10+ items/day consistently
- < 5 minutes spent on triage/review
- Work on 2+ items via editing mode weekly
- Zero data loss incidents

### Technical Metrics
- 99% uptime (local services)
- < 100ms API response time (p50)
- < 5s classification time (p95)
- < 1s sync latency

### Quality Metrics
- 90%+ classification accuracy
- 80%+ test coverage
- Zero P0 bugs after Week 5
- Clean separation of concerns (services independent)

## Launch Checklist

Before considering MVP "done":
- [ ] All validation criteria pass
- [ ] Documentation complete (setup, user manual)
- [ ] No known P0/P1 bugs
- [ ] Performance acceptable (< 5s for all operations)
- [ ] Data backup/export working
- [ ] Error handling graceful (no crashes)
- [ ] Used personally for 1 week without major issues

**When complete:** Share with close friends/beta testers for feedback
