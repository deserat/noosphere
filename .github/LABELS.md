# GitHub Labels Configuration

This document defines all labels used in the Noosphere project for issue and PR management.

## Creating Labels

### Using GitHub Web UI
1. Go to: `https://github.com/deserat/noosphere/labels`
2. Click "New label"
3. Enter name, description, and color from tables below
4. Click "Create label"

### Using GitHub CLI

```bash
# Type Labels
gh label create "type/epic" --description "High-level feature grouping (maps to EPIC-X)" --color "8B5CF6"
gh label create "type/story" --description "User story from Phase 1 roadmap (EPIC-X-Y)" --color "3B82F6"
gh label create "type/task" --description "Individual task or subtask within a story" --color "10B981"
gh label create "type/bug" --description "Something isn't working as expected" --color "EF4444"
gh label create "type/enhancement" --description "Improvement to existing functionality" --color "F59E0B"
gh label create "type/docs" --description "Documentation updates or additions" --color "6B7280"
gh label create "type/refactor" --description "Code restructuring without behavior change" --color "8B5CF6"

# Priority Labels
gh label create "priority/P0" --description "Critical path - blocks other work" --color "DC2626"
gh label create "priority/P1" --description "Core foundation - must complete in Phase 1" --color "F97316"
gh label create "priority/P2" --description "Important but can parallelize with other work" --color "FBBF24"
gh label create "priority/P3" --description "Nice to have - post-Phase 1" --color "84CC16"

# Service Labels
gh label create "service/api-service" --description "FastAPI Python backend service" --color "06B6D4"
gh label create "service/cli" --description "Ratatui TUI Rust client" --color "A855F7"
gh label create "service/sync-service" --description "File watching Rust background service" --color "EC4899"
gh label create "service/database" --description "PostgreSQL schema, migrations, or queries" --color "14B8A6"
gh label create "service/vault" --description "File vault markdown/YAML structure" --color "F97316"
gh label create "service/docs" --description "Documentation only changes" --color "6B7280"
gh label create "service/infra" --description "Infrastructure, deployment, or tooling" --color "78716C"

# Status Labels
gh label create "status/blocked" --description "Waiting on dependencies or external factors" --color "DC2626"
gh label create "status/ready" --description "All dependencies met, ready to start" --color "10B981"
gh label create "status/in-progress" --description "Currently being worked on" --color "3B82F6"
gh label create "status/in-review" --description "PR submitted, awaiting code review" --color "F59E0B"
gh label create "status/needs-info" --description "Requires clarification or additional information" --color "8B5CF6"

# Size Labels
gh label create "size/XS" --description "1-2 story points - trivial change" --color "D1FAE5"
gh label create "size/S" --description "3 story points - small feature" --color "BBF7D0"
gh label create "size/M" --description "5 story points - medium feature" --color "FEF3C7"
gh label create "size/L" --description "8 story points - large feature" --color "FED7AA"
gh label create "size/XL" --description "13 story points - very large feature" --color "FECACA"

# Phase Labels
gh label create "phase/1-foundation" --description "Phase 1: Repository, database, vault, scaffolding" --color "3B82F6"
gh label create "phase/2-ai-classification" --description "Phase 2: AI classification, tagging, embeddings" --color "8B5CF6"
gh label create "phase/3-surfacing" --description "Phase 3: Cadence-based surfacing, intelligence" --color "EC4899"
gh label create "phase/4-polish" --description "Phase 4: Distribution, performance, tutorials" --color "10B981"

# Dependency Labels
gh label create "dependencies/has-blockers" --description "This issue blocks other work" --color "DC2626"
gh label create "dependencies/blocked-by" --description "Blocked by other issues (see description)" --color "F97316"
```

## Label Schema Reference

### Type Labels
| Name | Color | Description |
|------|-------|-------------|
| type/epic | `#8B5CF6` (Purple) | High-level feature grouping (maps to EPIC-X) |
| type/story | `#3B82F6` (Blue) | User story from Phase 1 roadmap (EPIC-X-Y) |
| type/task | `#10B981` (Green) | Individual task or subtask within a story |
| type/bug | `#EF4444` (Red) | Something isn't working as expected |
| type/enhancement | `#F59E0B` (Amber) | Improvement to existing functionality |
| type/docs | `#6B7280` (Gray) | Documentation updates or additions |
| type/refactor | `#8B5CF6` (Purple) | Code restructuring without behavior change |

### Priority Labels
| Name | Color | Description |
|------|-------|-------------|
| priority/P0 | `#DC2626` (Dark Red) | Critical path - blocks other work |
| priority/P1 | `#F97316` (Orange) | Core foundation - must complete in Phase 1 |
| priority/P2 | `#FBBF24` (Yellow) | Important but can parallelize with other work |
| priority/P3 | `#84CC16` (Lime) | Nice to have - post-Phase 1 |

### Service Labels
| Name | Color | Description |
|------|-------|-------------|
| service/api-service | `#06B6D4` (Cyan) | FastAPI Python backend service |
| service/cli | `#A855F7` (Purple) | Ratatui TUI Rust client |
| service/sync-service | `#EC4899` (Pink) | File watching Rust background service |
| service/database | `#14B8A6` (Teal) | PostgreSQL schema, migrations, or queries |
| service/vault | `#F97316` (Orange) | File vault markdown/YAML structure |
| service/docs | `#6B7280` (Gray) | Documentation only changes |
| service/infra | `#78716C` (Stone) | Infrastructure, deployment, or tooling |

### Status Labels
| Name | Color | Description |
|------|-------|-------------|
| status/blocked | `#DC2626` (Red) | Waiting on dependencies or external factors |
| status/ready | `#10B981` (Green) | All dependencies met, ready to start |
| status/in-progress | `#3B82F6` (Blue) | Currently being worked on |
| status/in-review | `#F59E0B` (Amber) | PR submitted, awaiting code review |
| status/needs-info | `#8B5CF6` (Purple) | Requires clarification or additional information |

### Size Labels
| Name | Color | Description |
|------|-------|-------------|
| size/XS | `#D1FAE5` (Light Green) | 1-2 story points - trivial change |
| size/S | `#BBF7D0` (Green) | 3 story points - small feature |
| size/M | `#FEF3C7` (Yellow) | 5 story points - medium feature |
| size/L | `#FED7AA` (Orange) | 8 story points - large feature |
| size/XL | `#FECACA` (Red) | 13 story points - very large feature |

### Phase Labels
| Name | Color | Description |
|------|-------|-------------|
| phase/1-foundation | `#3B82F6` (Blue) | Phase 1: Repository, database, vault, scaffolding |
| phase/2-ai-classification | `#8B5CF6` (Purple) | Phase 2: AI classification, tagging, embeddings |
| phase/3-surfacing | `#EC4899` (Pink) | Phase 3: Cadence-based surfacing, intelligence |
| phase/4-polish | `#10B981` (Green) | Phase 4: Distribution, performance, tutorials |

### Dependency Labels
| Name | Color | Description |
|------|-------|-------------|
| dependencies/has-blockers | `#DC2626` (Red) | This issue blocks other work |
| dependencies/blocked-by | `#F97316` (Orange) | Blocked by other issues (see description) |

## Usage Guidelines

### Every Issue Must Have
1. **Type** label (epic, story, task, bug, enhancement, docs, or refactor)
2. **Priority** label (P0, P1, P2, or P3)
3. **At least one Service** label (api-service, cli, sync-service, database, vault, docs, or infra)

### Optional Labels
- **Size** labels for stories and tasks (helps with estimation)
- **Status** labels for workflow tracking
- **Phase** labels for roadmap alignment
- **Dependency** labels when issues block or are blocked by others

### Multiple Service Labels
Issues often span multiple services. For example:
- Full-stack feature: `service/api-service` + `service/cli`
- Database + API work: `service/database` + `service/api-service`
- Documentation update: `service/docs` (only one service)

### Status Workflow
```
(No status) → status/ready → status/in-progress → status/in-review → (Closed)
```

Special states:
- `status/blocked` - Has unresolved dependencies
- `status/needs-info` - Requires clarification from reporter or team
