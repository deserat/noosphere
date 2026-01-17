# Phase 1 User Stories and Epics

This directory contains user stories and epics for **Phase 1: Foundation** of the Noosphere implementation roadmap. Phase 1 establishes the core infrastructure: project structure, database, file vault, configuration, and basic service scaffolding.

## Epic Overview

Phase 1 is divided into 5 epics covering different functional areas:

### Epic 1: Development Environment Setup
**Goal**: Establish complete development infrastructure for multi-language project
**Value**: Enables team to begin development with proper tooling, standards, and documentation
**Story Count**: 3 stories
**Total Points**: 11 points

### Epic 2: Database Foundation
**Goal**: Production-ready PostgreSQL database with vector search capability
**Value**: Provides persistent storage layer with AI-ready semantic search infrastructure
**Story Count**: 3 stories
**Total Points**: 23 points

### Epic 3: File Vault System
**Goal**: File-based knowledge vault with safe concurrent access
**Value**: Enables markdown-based knowledge storage with external tool compatibility
**Story Count**: 2 stories
**Total Points**: 13 points

### Epic 4: Configuration Management
**Goal**: Flexible configuration system supporting multiple environments
**Value**: Enables environment-specific settings without code changes
**Story Count**: 2 stories
**Total Points**: 8 points

### Epic 5: Service Scaffolding
**Goal**: Minimal but functional API and sync services
**Value**: Proves architecture viability and service communication patterns
**Story Count**: 3 stories
**Total Points**: 19 points

**Phase 1 Total**: 13 stories, 74 story points

## Story List

### Epic 1: Development Environment Setup (11 points)

| Story | Title | Priority | Points |
|-------|-------|----------|--------|
| [EPIC-1-1](EPIC-1-1-repository-structure.md) | Repository Structure and Documentation Framework | P0 | 3 |
| [EPIC-1-2](EPIC-1-2-development-environments.md) | Python and Rust Development Environment Setup | P0 | 5 |
| [EPIC-1-3](EPIC-1-3-development-tooling.md) | Development Tooling and Quality Gates | P2 | 3 |

### Epic 2: Database Foundation (23 points)

| Story | Title | Priority | Points |
|-------|-------|----------|--------|
| [EPIC-2-1](EPIC-2-1-database-setup.md) | PostgreSQL with pgvector Installation and Configuration | P0 | 5 |
| [EPIC-2-2](EPIC-2-2-database-models-migrations.md) | SQLAlchemy Models and Migration System | P1 | 13 |
| [EPIC-2-3](EPIC-2-3-database-connection-seed.md) | Database Connection Module and Seed Data | P1 | 5 |

### Epic 3: File Vault System (13 points)

| Story | Title | Priority | Points |
|-------|-------|----------|--------|
| [EPIC-3-1](EPIC-3-1-vault-structure-utilities.md) | Vault Directory Structure and Markdown Utilities | P1 | 8 |
| [EPIC-3-2](EPIC-3-2-file-locking.md) | File Locking Mechanism for Concurrent Access | P2 | 5 |

### Epic 4: Configuration Management (8 points)

| Story | Title | Priority | Points |
|-------|-------|----------|--------|
| [EPIC-4-1](EPIC-4-1-configuration-system.md) | YAML Configuration System for Both Services | P1 | 3 |
| [EPIC-4-2](EPIC-4-2-configuration-loaders.md) | Configuration Loaders with Environment Variable Support | P1 | 5 |

### Epic 5: Service Scaffolding (19 points)

| Story | Title | Priority | Points |
|-------|-------|----------|--------|
| [EPIC-5-1](EPIC-5-1-api-service-scaffolding.md) | FastAPI Service with Health Check and Scheduler | P1 | 8 |
| [EPIC-5-2](EPIC-5-2-sync-service-scaffolding.md) | Rust Sync Service with File Watching | P1 | 8 |
| [EPIC-5-3](EPIC-5-3-service-startup-verification.md) | Service Startup Scripts and End-to-End Verification | P2 | 3 |

## Priority Distribution

- **P0 (Critical Path)**: 3 stories, 13 points
  - Must complete first, blocks all other work
  - Repository structure, development environments, database setup

- **P1 (Core Foundation)**: 7 stories, 47 points
  - Essential Phase 1 functionality
  - Database models, vault utilities, configuration, service scaffolding

- **P2 (Important but Parallelizable)**: 3 stories, 14 points
  - Can be completed in parallel with P1 stories
  - Development tooling, file locking, startup scripts

## Dependency Graph

```
Critical Path (P0):
EPIC-1-1 (Repository Structure) ─────┐
                                     ├──> All other stories
EPIC-1-2 (Development Environments) ─┤
                                     │
EPIC-2-1 (Database Setup) ───────────┘

Core Foundation (P1):
EPIC-2-1 ──> EPIC-2-2 (Database Models) ──> EPIC-2-3 (DB Connection)
                                                 │
EPIC-1-1 ──> EPIC-3-1 (Vault Structure) ────────┤
                                                 ├──> EPIC-5-1 (API Service)
EPIC-1-1 ──> EPIC-4-1 (Config System) ──> EPIC-4-2 (Config Loaders) ──┤
                                                                       │
EPIC-1-2 ──────────────────────────────────────────────────────────────┤
                                                                       │
                                                         EPIC-5-1 ──> EPIC-5-2 (Sync Service)
                                                                       │
                                                         EPIC-5-2 ──> EPIC-5-3 (Startup Scripts)

Parallelizable (P2):
EPIC-1-3 (Development Tooling) ─── Can be done anytime after EPIC-1-1
EPIC-3-2 (File Locking) ─────────── Can be done anytime after EPIC-3-1
EPIC-5-3 (Startup Scripts) ──────── Must wait for EPIC-5-1 and EPIC-5-2
```

## Implementation Order

### Phase 1A: Foundation (P0 - Week 1)
1. **EPIC-1-1**: Repository Structure (3 points) - *Blocks everything*
2. **EPIC-1-2**: Development Environments (5 points) - *Enables coding*
3. **EPIC-2-1**: Database Setup (5 points) - *Enables database work*

**Deliverable**: Repository structure exists, development environments ready, database accessible

### Phase 1B: Core Infrastructure (P1 - Weeks 2-3)
4. **EPIC-2-2**: Database Models (13 points) - *Complex, do first*
5. **EPIC-4-1**: Configuration System (3 points) - *Quick win*
6. **EPIC-3-1**: Vault Structure (8 points) - *Parallel with config*
7. **EPIC-4-2**: Configuration Loaders (5 points) - *After config system*
8. **EPIC-2-3**: Database Connection (5 points) - *After models*

**Deliverable**: Database schema complete, vault structure exists, configuration system working

### Phase 1C: Services (P1 - Week 4)
9. **EPIC-5-1**: API Service (8 points) - *Do first*
10. **EPIC-5-2**: Sync Service (8 points) - *After API service*

**Deliverable**: Both services running and communicating

### Phase 1D: Polish (P2 - Week 5)
11. **EPIC-1-3**: Development Tooling (3 points)
12. **EPIC-3-2**: File Locking (5 points)
13. **EPIC-5-3**: Startup Scripts (3 points)

**Deliverable**: Complete Phase 1 system with tooling and verification

## Mapping to Phase 1 Exit Criteria

The following table maps Phase 1 exit criteria (from implementation-roadmap.md) to user stories:

| Exit Criteria | Stories |
|---------------|---------|
| Repository structure with clean service separation | EPIC-1-1 |
| Development environments (Python + Rust) fully configured | EPIC-1-2 |
| PostgreSQL with pgvector installed and accessible | EPIC-2-1 |
| Database schema (9 tables) created via migrations | EPIC-2-2 |
| Seed data available for testing | EPIC-2-3 |
| File vault structure (~/.noosphere-vault) with category folders | EPIC-3-1 |
| Markdown frontmatter utilities (parse, write, template) | EPIC-3-1 |
| Lock file mechanism prevents concurrent access issues | EPIC-3-2 |
| Configuration system (YAML + env vars) for both services | EPIC-4-1, EPIC-4-2 |
| FastAPI service runs with health check endpoint | EPIC-5-1 |
| Background scheduler configured (not yet fully functional) | EPIC-5-1 |
| Rust sync service watches vault and detects changes | EPIC-5-2 |
| File changes logged (actual sync implementation in Phase 2) | EPIC-5-2 |
| Services start via scripts and communicate | EPIC-5-3 |
| Verification script confirms Phase 1 completion | EPIC-5-3 |

**All 15 Phase 1 roadmap sections are covered by these 13 user stories.**

## Story Point Estimation Guide

For reference, the story point scale used:

- **1-2 points**: Simple file creation, basic configuration (1-2 hours)
- **3-5 points**: Module development with tests (4-8 hours)
- **8-13 points**: Complex system integration (1-3 days)

Estimates assume experienced developer with appropriate tools and clear requirements.

## Getting Started

To begin implementation:

1. **Read the Implementation Roadmap**: [implementation-roadmap.md](../implementation-roadmap.md)
2. **Review Epic Breakdown**: Understand the 5 epic groupings above
3. **Start with P0 Stories**: Complete EPIC-1-1, EPIC-1-2, EPIC-2-1 first
4. **Follow Dependencies**: Use the dependency graph to sequence remaining work
5. **Verify Completion**: Run `./verify-phase1.sh` (from EPIC-5-3) to confirm Phase 1 done

## Story Template

Each story file follows this structure:

```markdown
# [Story Title]

**Epic**: [Epic Name]
**Priority**: P0/P1/P2
**Story Points**: [1-13]

## User Story
[As a... I need... So that...]

## Acceptance Criteria
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

## Technical Notes
- Implementation details
- Technology choices
- Considerations

## Dependencies
- **Blocks**: Stories that can't start until this completes
- **Blocked By**: Stories that must complete before this can start
- **Related**: Stories that can run in parallel

## Verification
How to test/verify story completion
```

## Phase 1 Success Metrics

Phase 1 is complete when:

- [ ] All 13 stories marked as done
- [ ] `./verify-phase1.sh` passes all tests
- [ ] Services start with `./start.sh` without errors
- [ ] Health check endpoint returns "healthy" status
- [ ] File changes in vault are detected by sync service
- [ ] Database contains seed data
- [ ] Documentation allows new developer to reproduce environment

## Next Steps

After Phase 1 completion, proceed to **Phase 2: AI Classification** which will:
- Implement AI classification for captured items
- Add actual sync logic (Phase 1 only detects changes)
- Create CLI for frictionless capture
- Implement surfacing job logic (Phase 1 only schedules it)

Phase 2 stories will be created after Phase 1 is complete and validated.

---

**Total Phase 1 Effort**: 74 story points (~3-5 weeks for 1 developer, ~2-3 weeks for 2 developers)

**Key Technologies**:
- **Backend**: Python 3.11+, FastAPI (standard conventions), SQLAlchemy, PostgreSQL 14+, pgvector
- **CLI**: Rust 1.70+, ratatui (Elm Architecture TUI), crossterm, tokio, reqwest
- **Sync Service**: Rust 1.70+, notify (file watching), tokio, reqwest
- **Database**: 9 tables with vector embeddings (pgvector)
- **Vault**: Markdown files with YAML frontmatter
- **Configuration**: YAML files with environment variable overrides

**Architecture Patterns**:
- **API Service**: FastAPI with `app/` layout (api/endpoints/, core/, db/, models/, schemas/, crud/, services/)
- **CLI**: Elm Architecture (Model-Update-View) with ratatui for TUI
- **Sync Service**: Event-driven file watching with async Rust
