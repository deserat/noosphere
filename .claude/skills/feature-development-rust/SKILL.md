---
name: feature-development-rust
description: Execute 11-step feature development workflow for Rust services (cli TUI and sync-service daemon) with GitHub integration, modern coverage tools (cargo-llvm-cov 80% target), and automated issue tracking. Use when starting Rust feature work, implementing CLI features, TUI components, file watching, or following structured development process for cli or sync-service.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Task, AskUserQuestion
user-invocable: true
---

# Feature Development Workflow - Rust (cli & sync-service)

**Services**: cli (ratatui TUI) OR sync-service (async daemon)
**Stack**: Rust 1.70+, ratatui, tokio, notify, reqwest
**MCP Tools**: sequential-thinking, context7
**Coverage**: 80% target

You are a feature development workflow orchestrator for Noosphere's **Rust services** (cli TUI and sync-service daemon). Guide developers through a structured 11-step process with quality gates and approval requirements.

## Project Context

- **Services**: cli (ratatui TUI) OR sync-service (async daemon)
- **Stack**: Rust 1.70+, ratatui, tokio, notify, reqwest
- **Formatting**: `cargo fmt`
- **Linting**: `cargo clippy --all-targets --all-features -- -D warnings`
- **Testing**: `cargo test --all-features --workspace`
- **Coverage**: `cargo llvm-cov --all-features --workspace --lcov --output-path lcov.info`
- **Coverage Requirement**: 80% target
- **Branch naming**: `feature/EPIC-X-Y-brief-description`
- **GitHub CLI**: `gh issue view EPIC-X-Y`

## MCP Tools Available

This agent can leverage the following MCP tools:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mcp__sequential-thinking__sequentialthinking` | Structured problem decomposition | Step 3: Planning complex features |
| `mcp__plugin_context7_context7__resolve-library-id` | Find library documentation IDs | Step 5: When using Rust crates |
| `mcp__plugin_context7_context7__query-docs` | Fetch current library docs | Step 5: Before implementing crate integrations |

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
   - Which service(s): cli, sync-service, or both
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

**Critical step to prevent convention mixing and select correct Rust service.**

**Determine which Rust service you're working on** based on issue labels:

**If service/cli (TUI application)**:
1. Read `cli/AGENTS.md` to load CLI-specific context
2. Display context summary:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Service Context Loaded: cli (TUI)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Language: Rust 1.70+
   Architecture: Elm Architecture (ratatui)
   Framework: ratatui (terminal UI)
   Patterns: Model-Update-View, keyboard event handling
   Directory: cli/

   All operations will be scoped to cli/ directory.
   ```
3. Confirm: **All operations use path="cli/"**

**If service/sync-service (Async daemon)**:
1. Read `sync-service/AGENTS.md` to load daemon-specific context
2. Display context summary:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Service Context Loaded: sync-service
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Language: Rust 1.70+
   Architecture: Async daemon
   Runtime: tokio (async runtime)
   Patterns: File watching (notify), async tasks
   Directory: sync-service/

   All operations will be scoped to sync-service/ directory.
   ```
3. Confirm: **All operations use path="sync-service/"**

4. Display: "Context loaded. Proceeding to planning..."

### Step 3: Create Implementation Plan (APPROVAL REQUIRED)

1. **Use sequential-thinking MCP tool** for structured problem decomposition:

   **For CLI features**:
   ```
   "Plan TUI feature for [feature name] using Elm Architecture (ratatui).
   Consider: Model state, Update logic, View rendering, keyboard event handling, terminal layout."
   ```

   **For sync-service features**:
   ```
   "Plan async daemon feature for [feature name] using tokio.
   Consider: File watching (notify), async task spawning, error handling, graceful shutdown."
   ```

   - Break down feature into logical implementation steps
   - Identify dependencies between components
   - Consider edge cases and potential issues
   - Generate structured thought process for the plan

2. **Use Explore subagent** to analyze existing patterns:

   **For CLI**:
   ```bash
   path="cli/src/"           # Main source
   path="cli/src/app.rs"     # Elm Architecture state
   path="cli/src/ui/"        # UI components
   ```

   **For sync-service**:
   ```bash
   path="sync-service/src/"          # Main source
   path="sync-service/src/watcher.rs" # File watching
   path="sync-service/src/tasks/"    # Async tasks
   ```

   - Existing patterns in codebase
   - Files that will need modification
   - Related components and dependencies

3. **Create detailed implementation plan** including:
   - Files to create/modify with rationale
   - Architecture decisions (why this approach?)
   - **For CLI**: UI components, state management, event handling
   - **For sync-service**: Async tasks, file watching, daemon lifecycle
   - Rust patterns (traits, enums, pattern matching)
   - Dependencies (Cargo.toml changes)
   - Error handling strategy

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

   **Format for CLI features**:
   ```markdown
   # EPIC-X-Y: Feature Title (CLI)

   ## Issue Reference
   - **GitHub Issue**: #ISSUE_NUMBER
   - **Epic**: EPIC-X
   - **Priority**: P0/P1/P2
   - **Story Points**: X
   - **Service**: cli

   ## Feature Summary
   [Brief description from issue]

   ## Implementation Plan

   ### Files to Create
   - `cli/src/ui/components/new_widget.rs` - New TUI widget

   ### Files to Modify
   - `cli/src/app.rs` - Add state for new feature
   - `cli/src/ui/mod.rs` - Register new component

   ### Architecture Decisions
   - Using Elm Architecture (Model-Update-View)
   - Keyboard shortcuts: Ctrl+N for new action

   ### State Changes
   - Add enum variant to `AppMode`
   - Add field to `App` struct

   ### UI Layout
   - New panel in main layout
   - Responsive terminal resizing

   ## Implementation Steps
   1. Define state types in app.rs
   2. Create UI component
   3. Add keyboard event handlers
   4. Update view rendering logic
   5. Write tests

   ## Testing Strategy
   - Unit tests for state transitions
   - Integration tests for keyboard events
   - Coverage target: 80%+

   ## Verification
   ```bash
   cd cli
   cargo run
   # Press Ctrl+N to test new feature
   ```
   ```

   **Format for sync-service features**:
   ```markdown
   # EPIC-X-Y: Feature Title (Sync Service)

   ## Issue Reference
   - **GitHub Issue**: #ISSUE_NUMBER
   - **Epic**: EPIC-X
   - **Priority**: P0/P1/P2
   - **Story Points**: X
   - **Service**: sync-service

   ## Feature Summary
   [Brief description from issue]

   ## Implementation Plan

   ### Files to Create
   - `sync-service/src/tasks/new_task.rs` - New async task

   ### Files to Modify
   - `sync-service/src/main.rs` - Spawn new task
   - `sync-service/src/watcher.rs` - Add file event handler

   ### Architecture Decisions
   - Using tokio::spawn for async task
   - File debouncing with notify crate

   ### Async Patterns
   - Use tokio::select! for cancellation
   - Graceful shutdown on SIGTERM

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

   ## Verification
   ```bash
   cd sync-service
   cargo run
   # Create test file in vault to trigger event
   ```
   ```

3. Post plan to GitHub issue as comment:
   ```bash
   gh issue comment EPIC-X-Y --body-file docs/dev/plans/EPIC-X-Y-brief-description.md
   ```

4. Display: "Implementation plan saved to docs/dev/plans/ and posted to GitHub issue. Proceeding to implementation..."

### Step 5: Begin Implementation

1. **Follow the approved plan exactly** - do not deviate without approval

2. **When using Rust crates, leverage Context7 MCP tools**:

   **Example for ratatui (CLI TUI)**:
   ```
   resolve-library-id: "ratatui"
   query-docs: libraryId="/ratatui/ratatui" query="event handling patterns"
   query-docs: libraryId="/ratatui/ratatui" query="layout constraints"
   query-docs: libraryId="/ratatui/ratatui" query="widget rendering"
   ```

   **Example for tokio (async runtime)**:
   ```
   resolve-library-id: "tokio"
   query-docs: libraryId="/tokio-rs/tokio" query="select! macro usage"
   query-docs: libraryId="/tokio-rs/tokio" query="graceful shutdown patterns"
   query-docs: libraryId="/tokio-rs/tokio" query="spawn vs spawn_blocking"
   ```

   **Example for notify (file watching)**:
   ```
   resolve-library-id: "notify"
   query-docs: libraryId="/notify-rs/notify" query="debouncer configuration"
   query-docs: libraryId="/notify-rs/notify" query="recursive watching"
   ```

   **Example for reqwest (HTTP client)**:
   ```
   resolve-library-id: "reqwest"
   query-docs: libraryId="/seanmonstar/reqwest" query="async client usage"
   ```

   This ensures you're using up-to-date Rust APIs and idiomatic patterns.

3. **Make logical, incremental changes**:
   - **For CLI**: models → update logic → view rendering → events
   - **For sync-service**: task modules → event handlers → integration
   - Run `cargo check` frequently to catch errors early

4. **Update Cargo.toml if adding dependencies**:
   ```bash
   cargo add <crate-name>
   # Cargo.lock will be updated automatically (must be committed)
   ```

5. **Keep files scoped to appropriate service**:
   - CLI: All operations in `cli/` directory
   - Sync: All operations in `sync-service/` directory
   - Use Read/Grep/Glob with `path="cli/"` or `path="sync-service/"`

6. **Keep user informed of progress**:
   - "Created new UI widget at cli/src/ui/components/resource_view.rs"
   - "Implemented async task at sync-service/src/tasks/sync_task.rs"
   - "Added dependency: tokio-util 0.7"

7. **Ask clarifying questions if requirements are unclear**

### Step 6: Run Linters, Formatting & Type Checking (QUALITY GATE)

**Change to service directory first** (cli/ or sync-service/):
```bash
cd [SERVICE_DIR]
```

Execute in order:
```bash
# Format code (auto-fixes)
cargo fmt

# Linting with clippy (comprehensive checks - all warnings as errors)
cargo clippy --all-targets --all-features -- -D warnings

# Additional clippy pedantic checks (optional but recommended)
cargo clippy --all-targets --all-features -- -W clippy::pedantic

# Check compilation without building
cargo check --all-targets --all-features
```

1. Display results clearly for each tool
2. If any failures:
   - **cargo fmt**: Should auto-fix, re-run `cargo fmt --check` to verify
   - **cargo clippy**: Fix all warnings (they're treated as errors with -D)
   - **cargo check**: Fix all compilation errors
   - Repeat until all pass
3. **DO NOT proceed to testing until all pass**
4. Display: "✓ All quality checks passed. Proceeding to testing..."

### Step 7: Write Tests

1. **Check existing test patterns** in service directory:
   - Unit tests: In same file or `tests/` module
   - Integration tests: `tests/` directory
   - Test utilities: `tests/common/mod.rs`

2. **Create tests for new functionality**:

   **Unit tests** (same file or tests module):
   ```rust
   #[cfg(test)]
   mod tests {
       use super::*;

       #[test]
       fn test_state_transition() {
           // Test pure logic
       }

       #[tokio::test]
       async fn test_async_function() {
           // Test async functions
       }
   }
   ```

   **Integration tests** (tests/ directory):
   ```rust
   // tests/integration_test.rs
   use cli::app::App;

   #[test]
   fn test_keyboard_event_handling() {
       // Test full flow
   }
   ```

3. **Follow Rust test conventions**:
   - Test functions: `fn test_*` or `#[test]`
   - Async tests: `#[tokio::test] async fn test_*`
   - Test modules: `#[cfg(test)] mod tests`

4. **Target 80%+ coverage for new code**:
   - Test happy paths
   - Test error cases (Result::Err, validation failures)
   - Test edge cases from implementation plan
   - Use `#[should_panic]` for panic tests

### Step 8: Run Tests with Coverage (QUALITY GATE)

**Install cargo-llvm-cov if not present**:
```bash
cargo install cargo-llvm-cov
```

**From service directory, run tests with coverage**:
```bash
# Run tests with coverage (generates lcov.info)
cargo llvm-cov --all-features --workspace --lcov --output-path lcov.info test

# Generate human-readable HTML report
cargo llvm-cov --all-features --workspace --html

# View summary (text output)
cargo llvm-cov --all-features --workspace --summary-only
```

**Alternative using cargo-tarpaulin** (Linux-friendly):
```bash
cargo install cargo-tarpaulin
cargo tarpaulin --all-features --workspace --out Html --out Xml --fail-under 80
```

1. **Coverage target: 80%+** (Rust's type system provides compile-time guarantees)
2. If failures or coverage below threshold:
   - **Analyze failure root cause** (don't just retry)
   - **Fix implementation** or **add missing tests**
   - **Re-run** until all pass AND coverage >= 80%
3. **Review coverage report**:
   - Check HTML report (`target/llvm-cov/html/index.html`)
   - Identify uncovered lines
   - Add tests for missing coverage
4. **ALL tests must pass with 80%+ coverage before proceeding**
5. Display: "✓ All tests passed with 80%+ coverage. Running final quality checks..."

**Why 80% for Rust?**:
- Type system catches many bugs at compile time
- Pattern matching exhaustiveness is enforced
- Some unsafe/macro-generated code is hard to test
- 80% is strong coverage for production Rust code

### Step 9: Final Quality Check (QUALITY GATE)

Run again to catch any changes from test fixes:

```bash
cd [SERVICE_DIR]

# Re-verify formatting (should be clean)
cargo fmt --check

# Re-run clippy (all warnings as errors)
cargo clippy --all-targets --all-features -- -D warnings

# Re-check compilation
cargo check --all-targets --all-features

# Run tests one more time (quick verification)
cargo test --all-features --workspace

# Documentation check (ensure all public items documented)
RUSTDOCFLAGS="-D warnings" cargo doc --all-features --workspace --no-deps
```

1. All must pass (should be clean from Step 6)
2. **DO NOT proceed if any fail** - fix and re-run
3. **Documentation check**: Ensures all public items have doc comments
   - Fix any missing documentation
   - Use `///` for public items
4. Check for Cargo.lock changes:
   - If dependencies were added, `Cargo.lock` must be committed
   - For applications (cli, sync-service), Cargo.lock is tracked in git
5. Display: "✓ Final quality checks passed. Preparing commit..."

### Step 10: Write Commit Message (APPROVAL REQUIRED)

1. **Summarize all changes made** during implementation
2. **Generate commit message** following Rust-specific format:

```
[EPIC-X-Y] Component: Brief description

Implementation:
- Added X module/struct/trait
- Implemented Y for Z
- Updated Cargo.toml dependencies (if applicable)

Acceptance criteria addressed:
- [ ] Criterion 1 from issue
- [ ] Criterion 2 from issue
- [ ] Criterion 3 from issue

Testing:
- Unit tests: X tests for core logic
- Integration tests: Y tests for full flow
- Coverage: XX% (target: 80%+)
- All clippy warnings resolved

Cargo changes:
- Added dependency: crate-name 0.x.y
- Updated Cargo.lock (committed)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Example for CLI**:
```
[EPIC-3-1] UI: Add resource view panel to TUI

Implementation:
- Created ResourceViewWidget in cli/src/ui/components/resource_view.rs
- Added ResourceViewMode to AppMode enum
- Implemented keyboard handler (Ctrl+R to toggle)
- Updated main layout to render new panel

Acceptance criteria addressed:
- [x] Resource list displayed in TUI panel
- [x] Keyboard navigation works (up/down arrows)
- [x] Panel toggles with Ctrl+R

Testing:
- Unit tests: 12 tests for widget rendering
- Integration tests: 5 tests for keyboard events
- Coverage: 85%
- All clippy warnings resolved

Cargo changes:
- No dependency changes
- Cargo.lock up to date

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Example for sync-service**:
```
[EPIC-4-2] Watcher: Add file change detection and API sync

Implementation:
- Created SyncTask in sync-service/src/tasks/sync_task.rs
- Implemented notify debouncer for file events
- Added graceful shutdown with tokio::select!
- Integrated with main daemon loop

Acceptance criteria addressed:
- [x] File changes detected within 1 second
- [x] API sync triggered on file change
- [x] Graceful shutdown on SIGTERM

Testing:
- Unit tests: 8 tests for sync logic
- Integration tests: 6 tests with temp files
- Coverage: 82%
- All clippy warnings resolved

Cargo changes:
- Added dependency: notify-debouncer-full 0.3
- Updated Cargo.lock (committed)

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

   **For CLI features**:
   ```bash
   gh pr create \
     --title "[EPIC-X-Y] Brief description (CLI)" \
     --body "$(cat <<'EOF'
   ## Summary
   [Brief description of TUI changes]

   ## Related Issue
   Closes #ISSUE_NUMBER (EPIC-X-Y)

   ## Changes
   - Added new UI widget for resource view
   - Implemented keyboard event handling (Ctrl+R)
   - Updated Elm Architecture state
   - Added terminal layout integration

   ## Testing
   - [x] Unit tests pass (widget logic)
   - [x] Integration tests pass (keyboard events)
   - [x] Coverage >= 80%
   - [x] Manual testing completed (TUI tested)
   - [x] All quality checks pass (clippy, fmt)

   ## Cargo Changes
   - No dependency changes / Added: notify-debouncer-full 0.3
   - Cargo.lock updated and committed

   ## Verification Steps
   ```bash
   cd cli
   cargo run
   # Press Ctrl+R to toggle resource view panel
   # Navigate with arrow keys
   # Verify panel rendering
   ```

   ## Checklist
   - [x] Code follows cli conventions (Elm Architecture)
   - [x] cli/AGENTS.md reviewed for context
   - [x] Documentation updated (if needed)
   - [x] All public items documented (cargo doc)
   - [x] No unsafe code added (or justified with SAFETY comments)
   EOF
   )" \
     --base develop
   ```

   **For sync-service features**:
   ```bash
   gh pr create \
     --title "[EPIC-X-Y] Brief description (Sync Service)" \
     --body "$(cat <<'EOF'
   ## Summary
   [Brief description of daemon changes]

   ## Related Issue
   Closes #ISSUE_NUMBER (EPIC-X-Y)

   ## Changes
   - Added file change detection with notify
   - Implemented async sync task
   - Added graceful shutdown handling
   - Integrated with daemon lifecycle

   ## Testing
   - [x] Unit tests pass (task logic)
   - [x] Integration tests pass (file watching)
   - [x] Coverage >= 80%
   - [x] Manual testing completed (daemon tested)
   - [x] All quality checks pass (clippy, fmt)

   ## Cargo Changes
   - Added: notify-debouncer-full 0.3
   - Cargo.lock updated and committed

   ## Verification Steps
   ```bash
   cd sync-service
   cargo run

   # In another terminal:
   touch ~/noosphere/vault/test.md  # Trigger file event
   # Check logs for sync trigger

   # Test graceful shutdown
   pkill -SIGTERM sync-service
   # Verify clean shutdown in logs
   ```

   ## Checklist
   - [x] Code follows sync-service conventions (async daemon)
   - [x] sync-service/AGENTS.md reviewed for context
   - [x] Documentation updated (if needed)
   - [x] All public items documented (cargo doc)
   - [x] Graceful shutdown tested
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
- **Quality gates are non-negotiable** - clippy/tests/coverage must pass
- **Coverage threshold**: 80% target (Rust's type system provides compile-time guarantees)
- **Approval checkpoints require explicit yes** - don't assume approval
- **Show progress clearly**: "Step X of 11: [StepName]"
- **Context isolation**: Always read correct AGENTS.md first (Step 2.5)
- **Service disambiguation**: Know whether you're in cli/ or sync-service/
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
5. **Use Context7 if crate-related** - fetch official Rust crate documentation

## Progress Display Format

Use this format at each step:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step X of 11: [Step Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Step content...]
```

## Rust-Specific Notes

**CLI Service Architecture** (Elm Architecture with ratatui):
- Models: `src/app.rs` - Application state (Model)
- Update: `src/app.rs` - State transitions (Update)
- View: `src/ui/` - Terminal rendering (View)
- Events: `src/app.rs` - Keyboard/terminal events
- Components: `src/ui/components/` - Reusable widgets

**Sync Service Architecture** (Async daemon):
- Main: `src/main.rs` - Daemon lifecycle
- Watcher: `src/watcher.rs` - File watching with notify
- Tasks: `src/tasks/` - Async background tasks
- Config: `src/config.rs` - Configuration management

**Always scope operations to correct service**:
- Read: `path="cli/"` or `path="sync-service/"`
- Grep: `path="cli/"` or `path="sync-service/"`
- Glob: `path="cli/"` or `path="sync-service/"`
- Task Explore: `path="cli/"` or `path="sync-service/"`

**Cargo.lock Management**:
- Both cli and sync-service are applications → Cargo.lock is tracked in git
- Always commit Cargo.lock changes with dependency updates
- Run `cargo update` only when explicitly updating dependencies

**Modern Rust Coverage Tools**:
- **Primary**: cargo-llvm-cov (LLVM-based, accurate, fast, 2023+ standard)
- **Alternative**: cargo-tarpaulin (Linux-focused, older but still valid)
