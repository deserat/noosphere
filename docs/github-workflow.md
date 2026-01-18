# GitHub Workflow Guide

This guide explains how to use GitHub issues, pull requests, and project management features for the Noosphere project.

## Quick Reference

### Issue Types
- **Epic**: High-level feature grouping → Use template "Epic"
- **Story**: User story from roadmap → Use template "User Story"
- **Bug**: Something broken → Use template "Bug Report"
- **Task**: Small unit of work → Use template "Task"

### Essential Labels
Every issue **must** have:
1. **Type** (epic/story/task/bug/enhancement/docs/refactor)
2. **Priority** (P0/P1/P2/P3)
3. **Service** (api-service/cli/sync-service/database/vault/docs/infra)

## Creating Issues

### Create an Epic

Epics group related stories for a major feature or phase.

**Title Format**: `EPIC-X: Descriptive epic name`

**Example**: `EPIC-1: Foundation Phase - Repository and Infrastructure`

**Steps**:
1. Go to Issues → New Issue → "Epic" template
2. Fill in Epic ID, phase, and description
3. List all related story issues (will add after stories are created)
4. Add service labels based on affected components
5. Set priority label (usually P0 or P1 for epics)
6. Assign to appropriate milestone (e.g., "Phase 1 - Foundation")

### Create a Story

Stories represent concrete user stories or implementation tasks.

**Title Format**: `Descriptive action-oriented title` (no EPIC prefix)

**Example**: `Configure Python and Rust development environments`

**Steps**:
1. Go to Issues → New Issue → "User Story" template
2. **Title**: Use semantic description (not [EPIC-X-Y] format)
3. **Story Reference**: Fill in EPIC-X, EPIC-X-Y, and story file path
4. Copy content from `docs/project/stories/EPIC-X-Y-name.md`
5. Add labels:
   - `type/story` (already added by template)
   - `priority/P[0-2]` (from story file)
   - `size/[XS-XL]` based on story points:
     - XS: 1-2 points
     - S: 3 points
     - M: 5 points
     - L: 8 points
     - XL: 13 points
   - `phase/1-foundation` (or appropriate phase)
   - Service labels (api-service, cli, sync-service, etc.)
6. Link dependencies in description
7. Assign to milestone

### Create a Bug Report

**Title Format**: `Descriptive bug title`

**Example**: `Classification returns null for empty content`

**Steps**:
1. Go to Issues → New Issue → "Bug Report" template
2. Fill in all sections (description, steps, expected/actual behavior)
3. Include environment details
4. Add service labels
5. Set priority (P0 for critical, P1 for important, P2 for minor)

### Create a Task

Tasks are small units of work, often subtasks of stories.

**Title Format**: `Descriptive task title`

**Example**: `Add pyright configuration to api-service`

**Steps**:
1. Go to Issues → New Issue → "Task" template
2. Describe what needs to be done
3. Link to parent story if applicable
4. Add service labels
5. Add size label for estimation (usually XS or S)

## Labels

### Label Categories

#### Type Labels (Required)
| Label | Description |
|-------|-------------|
| type/epic | High-level feature grouping |
| type/story | User story from roadmap |
| type/task | Individual task or subtask |
| type/bug | Something broken |
| type/enhancement | Improvement to existing feature |
| type/docs | Documentation changes |
| type/refactor | Code restructuring |

#### Priority Labels (Required)
| Label | Description | When to Use |
|-------|-------------|-------------|
| priority/P0 | Critical path - blocks other work | Blockers, critical bugs |
| priority/P1 | Core foundation - must complete in phase | Essential features |
| priority/P2 | Important but can parallelize | Nice-to-have features |
| priority/P3 | Post-phase work | Future enhancements |

#### Service Labels (Required - Multiple Allowed)
| Label | Description |
|-------|-------------|
| service/api-service | FastAPI Python backend |
| service/cli | Ratatui TUI Rust client |
| service/sync-service | File watching Rust service |
| service/database | PostgreSQL schema/migrations |
| service/vault | File vault structure |
| service/docs | Documentation only |
| service/infra | Infrastructure/tooling |

**Multiple Service Example**:
- Full-stack feature: `service/api-service` + `service/cli`
- Database + API: `service/database` + `service/api-service`

#### Status Labels (Optional - Workflow)
| Label | Description |
|-------|-------------|
| status/ready | Dependencies met, ready to start |
| status/in-progress | Currently being worked on |
| status/in-review | PR open, awaiting review |
| status/blocked | Waiting on dependencies |
| status/needs-info | Requires clarification |

#### Size Labels (Optional - Estimation)
| Label | Story Points | Description |
|-------|--------------|-------------|
| size/XS | 1-2 | Trivial change |
| size/S | 3 | Small feature |
| size/M | 5 | Medium feature |
| size/L | 8 | Large feature |
| size/XL | 13 | Very large feature |

#### Phase Labels (Optional - Roadmap)
| Label | Description |
|-------|-------------|
| phase/1-foundation | Repository, database, vault, scaffolding |
| phase/2-ai-classification | AI classification, tagging, embeddings |
| phase/3-surfacing | Cadence-based surfacing, intelligence |
| phase/4-polish | Distribution, performance, tutorials |

## Workflow States

### Issue Lifecycle

```
┌─────────┐
│ Backlog │ (Open issue, no status label)
└────┬────┘
     │ Dependencies resolved
     ▼
┌─────────┐
│  Ready  │ (Add status/ready label)
└────┬────┘
     │ Developer starts work
     ▼
┌──────────────┐
│ In Progress  │ (Add status/in-progress, remove status/ready)
└──────┬───────┘
       │ PR created
       ▼
┌──────────────┐
│  In Review   │ (Add status/in-review, remove status/in-progress)
└──────┬───────┘
       │ PR merged
       ▼
┌──────────────┐
│     Done     │ (Issue closed, remove all status labels)
└──────────────┘
```

### Special States

**Blocked**:
1. Add `status/blocked` label
2. Add comment explaining what blocks the issue
3. Link to blocking issue(s)
4. Update dependent issues with `dependencies/blocked-by` label

**Needs Info**:
1. Add `status/needs-info` label
2. Add comment with questions
3. @ mention person who can provide info

## Working on Issues

### Starting Work

```bash
# 1. Find a ready issue
# Look for issues with status/ready label and your service (e.g., service/cli)

# 2. Assign yourself to the issue
# Click "Assignees" → Add yourself

# 3. Update status labels
# Remove: status/ready
# Add: status/in-progress

# 4. Create feature branch (git-flow)
git checkout develop
git pull origin develop
git checkout -b feature/EPIC-1-2-dev-environments

# 5. Start work
# Follow coding standards in docs/agents/standards.md
```

### Making Commits

```bash
# Reference issue number in commits
git commit -m "feat(api): add health check endpoint

Part of #12 (EPIC-5-1 story)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Commit Message Format**:
- **Prefix**: feat/fix/docs/refactor/test/chore
- **Scope**: (api/cli/sync/db/vault/docs)
- **Reference**: Part of #[issue-number]

### Creating Pull Requests

```bash
# 1. Push branch
git push -u origin feature/EPIC-1-2-dev-environments

# 2. Open PR on GitHub
# Use PR template (auto-loads)

# 3. PR Title
# Use semantic description matching the issue title
# Example: "Configure Python and Rust development environments"

# 4. Fill in PR description
# - Closes #[issue-number]
# - Reference EPIC-X-Y in description
# - Check service boxes
# - Fill in changes, testing, verification

# 5. PR labels (auto-applied)
# Service labels auto-applied based on file paths
# Manually add type/bug, type/enhancement, etc. if needed

# 6. Request review
# Assign reviewers familiar with affected services
```

### Reviewing Pull Requests

**Reviewer Checklist**:
- [ ] Code follows standards (ruff/pyright for Python, clippy for Rust)
- [ ] Tests added/updated and passing
- [ ] Acceptance criteria from issue met
- [ ] Documentation updated if needed
- [ ] AGENTS.md updated if service boundaries changed
- [ ] No breaking changes (or documented)
- [ ] Verification steps work

**Approval**:
1. Click "Review changes"
2. Add comments or approve
3. Approve → PR merges to develop (if using auto-merge)

### Merging

```bash
# Merge using --no-ff (git-flow standard)
git checkout develop
git merge --no-ff feature/EPIC-1-2-dev-environments
git push origin develop

# Delete feature branch
git branch -d feature/EPIC-1-2-dev-environments
git push origin --delete feature/EPIC-1-2-dev-environments
```

**After Merge**:
- Issue auto-closes (via "Closes #XX" in PR)
- status/in-review label removed automatically
- Verify acceptance criteria met
- Add comment with verification results

## Sprint Planning

### Planning a Sprint

**Steps**:
1. Filter by `status/ready`
2. Sort by `priority/P0` → `priority/P1` → `priority/P2`
3. Check story points totals
4. Balance across services (avoid all API, no CLI work)
5. Assign issues to developers
6. Move to "In Progress" column on project board

### Using Milestones

**Phase 1 - Foundation** (Current):
- 13 stories
- 74 total story points
- Due: [Set based on team velocity]

**Viewing Milestone Progress**:
- Go to Issues → Milestones → "Phase 1 - Foundation"
- See open/closed issue counts
- Track story points completed

## GitHub CLI Tips

```bash
# Create issue from story file
gh issue create \
  --title "Configure Python and Rust development environments" \
  --body-file docs/project/stories/EPIC-1-2-development-environments.md \
  --label "type/story,priority/P0,phase/1-foundation,service/api-service,service/cli,size/M" \
  --milestone "Phase 1 - Foundation"

# List ready issues
gh issue list --label "status/ready"

# List your assigned issues
gh issue list --assignee "@me"

# Move issue to in-progress
gh issue edit 42 \
  --add-label "status/in-progress" \
  --remove-label "status/ready"

# View issue details
gh issue view 42

# Create PR
gh pr create \
  --title "Configure Python and Rust development environments" \
  --body "Closes #42

Part of EPIC-1-2 (Development Environments story)" \
  --base develop

# List PRs
gh pr list

# Review PR
gh pr review 15 --approve --body "LGTM! Acceptance criteria met."
```

## Project Board

### Setting Up Board (GitHub Projects Beta)

**Views**:
1. **Board View**: Kanban by status (Backlog → Ready → In Progress → In Review → Done)
2. **Service View**: Group by service label
3. **Priority View**: Sort by P0 → P1 → P2
4. **Sprint View**: Filter by current milestone

**Custom Fields**:
- Story Points (number)
- Epic ID (single select: EPIC-1, EPIC-2, etc.)
- Services (multi-select)
- Blocked By (text)

### Board Columns

| Column | Description | Status Label |
|--------|-------------|--------------|
| Backlog | Not ready to start | (none) |
| Ready | Dependencies met | status/ready |
| In Progress | Currently working | status/in-progress |
| In Review | PR open | status/in-review |
| Done | Completed & merged | (closed) |

## Troubleshooting

### Issue Not Auto-Closing from PR

**Problem**: PR merged but issue still open

**Solution**:
1. Check PR description has `Closes #XX` or `Fixes #XX`
2. Ensure issue number is correct
3. PR must merge to default branch (develop)
4. Manually close issue and reference PR

### Labels Not Auto-Applying to PR

**Problem**: Service labels not added automatically

**Solution**:
1. Check `.github/labeler.yml` has correct paths
2. Verify `.github/workflows/auto-label.yml` is active
3. Manually add service labels
4. Check workflow runs: Actions tab → "Auto Label PR"

### Issue Blocked

**Steps**:
1. Add `status/blocked` label
2. Add comment: "Blocked by #[issue-number] - [reason]"
3. Add `dependencies/blocked-by` label to issue
4. Add `dependencies/has-blockers` label to blocking issue
5. Update dependent issues

## Best Practices

### Label Hygiene
- Always add type, priority, and service labels
- Remove status labels when state changes
- Use multiple service labels for cross-service work
- Update size labels if scope changes

### Dependency Management
- Document dependencies in issue description
- Update when blockers resolve
- Keep dependency labels current

### Code Review
- Review against acceptance criteria (not just code quality)
- Check AGENTS.md for service boundaries
- Verify tests and documentation
- Ensure standards compliance

### Sprint Hygiene
- Update status labels daily
- Review blocked issues weekly
- Close completed issues with verification
- Archive done milestones monthly

## Related Documentation

- [Setup Guide](setup.md) - Development environment setup
- [Coding Standards](agents/standards.md) - Code style and quality
- [Implementation Roadmap](project/implementation-roadmap.md) - Development phases
- [Label Configuration](.github/LABELS.md) - Complete label reference
