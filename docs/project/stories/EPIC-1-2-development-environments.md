# Development Environment Setup

**Epic**: Development Environment Setup
**Priority**: P0
**Story Points**: 5

## User Story

As a developer,
I need properly configured Python and Rust development environments,
So that I can build, run, and test both the API service and client applications locally.

## Acceptance Criteria

### Python Environment (API Service)
- [ ] uv package manager installed and verified:
  ```bash
  uv --version
  ```
- [ ] Python virtual environment created for api-service:
  ```bash
  cd api-service
  uv venv
  ```
- [ ] `requirements.txt` created with all necessary dependencies:
  - **Web Framework**: FastAPI, uvicorn
  - **Database**: SQLAlchemy, alembic, psycopg2-binary, pgvector
  - **AI**: litellm
  - **Utilities**: python-dotenv, pydantic, pyyaml, watchdog
- [ ] Dependencies installed successfully:
  ```bash
  source .venv/bin/activate
  uv sync
  ```
- [ ] Python version documented (3.14+)
- [ ] Virtual environment activation instructions in docs/setup.md
- [ ] uv installation instructions in docs/setup.md

### Rust Environment (CLI + Sync Service)
- [ ] Rust toolchain verified (1.70+ required):
  ```bash
  rustc --version
  cargo --version
  ```
- [ ] CLI Cargo project initialized with Elm Architecture TUI setup:
  - `cli/Cargo.toml` created with metadata and dependencies:
    ```toml
    [package]
    name = "noosphere-cli"
    version = "0.1.0"
    edition = "2021"

    [dependencies]
    # TUI Framework (Elm Architecture)
    ratatui = "0.26"
    crossterm = "0.27"

    # Async runtime
    tokio = { version = "1.35", features = ["full"] }

    # API client
    reqwest = { version = "0.11", features = ["json"] }

    # Serialization
    serde = { version = "1.0", features = ["derive"] }
    serde_json = "1.0"

    # CLI argument parsing
    clap = { version = "4.4", features = ["derive"] }

    # Error handling
    anyhow = "1.0"
    thiserror = "1.0"

    # Logging
    tracing = "0.1"
    tracing-subscriber = "0.3"

    [[bin]]
    name = "noosphere"
    path = "src/main.rs"
    ```
- [ ] CLI module structure created following Elm Architecture:
  - `src/main.rs` (event loop)
  - `src/app.rs` (Model - application state)
  - `src/ui.rs` (View - rendering)
  - `src/handler.rs` (Update - event handlers)
  - `src/event.rs` (event types)
  - `src/tui.rs` (terminal setup)
  - `src/components/mod.rs` (UI components)
  - `src/api/mod.rs` (API client)
- [ ] CLI project compiles successfully:
  ```bash
  cd cli
  cargo build
  ```
- [ ] Sync service Cargo project initialized:
  - `sync-service/Cargo.toml` created with dependencies:
    - tokio (async runtime)
    - reqwest (HTTP client)
    - serde, serde_json, serde_yaml (serialization)
    - notify (file watching)
    - sha2 (content hashing)
- [ ] Sync service compiles successfully:
  ```bash
  cd sync-service
  cargo build
  ```
- [ ] Minimal module files created for CLI (Elm Architecture stubs):
  - `src/main.rs` (event loop skeleton with module declarations)
  - `src/app.rs` (empty App struct placeholder)
  - `src/ui.rs` (empty render function placeholder)
  - `src/handler.rs` (empty event handler placeholder)
  - `src/event.rs` (empty event types placeholder)
  - `src/tui.rs` (empty terminal setup placeholder)
  - `src/components/mod.rs` (empty components module)
  - `src/api/mod.rs` (empty API client module)
- [ ] Minimal main.rs file created for sync service:
  - Basic async main function skeleton

### Environment Validation
- [ ] `.env.example` file created in root with documented environment variables:
  ```
  # Database
  DATABASE_URL=postgresql://user:password@localhost:5432/noosphere

  # Vault
  VAULT_PATH=~/noosphere-vault

  # API Configuration
  API_HOST=localhost
  API_PORT=8000

  # AI Configuration (optional for Phase 1)
  # ANTHROPIC_API_KEY=your-key-here
  # OPENAI_API_KEY=your-key-here
  ```
- [ ] Setup verification script works (can be simple bash script):
  ```bash
  # Check Python
  python3 --version

  # Check Rust
  cargo --version

  # Check Python venv
  which python  # Should point to .venv

  # Check Rust compilation
  cd cli && cargo check && cd ..
  cd sync-service && cargo check && cd ..
  ```

## Technical Notes

**Python Requirements Management**:
- Use `uv` package manager for fast, reliable dependency resolution
- `uv sync` creates `uv.lock` file for reproducible dependency resolution
- Use specific version ranges in `requirements.txt`: `fastapi>=0.104.1,<0.105.0`
- `uv.lock` file should be committed to git for exact version reproducibility
- Document Python 3.14+ requirement (latest stable with improved performance)
- uv manages Python versions: `uv python install 3.14`

**Rust Dependencies**:
- Use `features = ["full"]` for tokio to enable all async features
- Use `features = ["json"]` for reqwest to enable JSON serialization
- Pin to minor versions to avoid breaking changes
- Cargo.lock should be committed for applications (not libraries)

**CLI Elm Architecture Pattern**:
The TUI follows the Elm Architecture for predictable state management:

1. **Model** (`app.rs`): Defines all application state
   ```rust
   pub struct App {
       pub current_view: View,
       pub selected_item: usize,
       pub input_buffer: String,
       pub items: Vec<Item>,
       pub should_quit: bool,
   }
   ```

2. **Update** (`handler.rs`): Pure functions handling state transitions
   ```rust
   pub fn handle_key_event(app: &mut App, key: KeyEvent) -> Result<()> {
       match key.code {
           KeyCode::Char('q') => app.should_quit = true,
           KeyCode::Down => app.selected_item += 1,
           // ... other handlers
       }
   }
   ```

3. **View** (`ui.rs`): Renders state to terminal
   ```rust
   pub fn render(app: &App, frame: &mut Frame) {
       let chunks = Layout::default()
           .direction(Direction::Vertical)
           .constraints([Constraint::Length(3), Constraint::Min(0)])
           .split(frame.size());

       render_header(app, frame, chunks[0]);
       render_list(app, frame, chunks[1]);
   }
   ```

4. **Event Loop** (`main.rs`): Poll → Update → Render
   ```rust
   loop {
       terminal.draw(|f| ui::render(&app, f))?;

       if let Event::Key(key) = event::poll()? {
           handler::handle_key_event(&mut app, key)?;
       }

       if app.should_quit {
           break;
       }
   }
   ```

**Minimal main.rs Templates**:

CLI (`cli/src/main.rs`) - Elm Architecture skeleton:
```rust
use anyhow::Result;

mod app;
mod ui;
mod handler;
mod event;
mod tui;

fn main() -> Result<()> {
    // Phase 1: Just verify structure compiles
    println!("Noosphere CLI - Elm Architecture TUI");
    println!("✓ Rust toolchain verified");
    println!("✓ ratatui dependencies ready");

    // Phase 2+: Actual TUI event loop will go here
    Ok(())
}
```

Sync Service (`sync-service/src/main.rs`):
```rust
#[tokio::main]
async fn main() {
    println!("Noosphere Sync Service - Development");
    println!("Async runtime verified");
}
```

**CLI Module Stubs** (for Phase 1 compilation):

`src/app.rs`:
```rust
// Model - Application state (placeholder)
pub struct App;

impl App {
    pub fn new() -> Self {
        Self
    }
}
```

`src/ui.rs`:
```rust
// View - Rendering logic (placeholder)
```

`src/handler.rs`:
```rust
// Update - Event handlers (placeholder)
```

`src/event.rs`:
```rust
// Event types and polling (placeholder)
```

`src/tui.rs`:
```rust
// Terminal setup/teardown (placeholder)
```

`src/components/mod.rs`:
```rust
// Reusable UI components (placeholder)
```

`src/api/mod.rs`:
```rust
// API client for backend communication (placeholder)
```

These stubs allow the project to compile in Phase 1. Full implementation comes in Phase 2+.

**Cross-Platform Considerations**:
- Python venv activation differs:
  - Linux/Mac: `source venv/bin/activate`
  - Windows: `venv\Scripts\activate`
- Document platform-specific instructions in docs/setup.md

## Dependencies

- **Blocks**:
  - EPIC-2-2 (Database models need SQLAlchemy installed)
  - EPIC-4-2 (Config loaders need dependencies installed)
  - EPIC-5-1 (API service scaffolding needs FastAPI)
  - EPIC-5-2 (Sync service needs notify crate)
- **Blocked By**:
  - EPIC-1-1 (Repository structure must exist first)
- **Related**:
  - EPIC-1-3 (Development tooling will add linting/formatting configs)

## Verification

**Python Environment Verification**:
```bash
cd api-service

# Verify uv is installed
uv --version
# Should output uv version

source .venv/bin/activate

# Check Python version
python --version
# Should output: Python 3.14.x or higher

# Verify all packages installed
uv pip list | grep -E "fastapi|uvicorn|sqlalchemy|alembic|litellm"

# Test imports
python -c "import fastapi; import sqlalchemy; import litellm; print('All imports successful')"

# Or use uv run (no activation needed)
uv run python -c "import fastapi; import sqlalchemy; import litellm; print('All imports successful')"

# Deactivate
deactivate
```

**Rust Environment Verification**:
```bash
# Check Rust version
rustc --version
# Should output: rustc 1.70.0 or higher

# Verify CLI compilation
cd cli
cargo build
cargo run
# Should output: "Noosphere CLI - Development"

# Verify sync service compilation
cd ../sync-service
cargo build
cargo run
# Should output: "Noosphere Sync Service - Development"

# Check dependencies are resolved
cargo tree | grep -E "tokio|reqwest|notify"
```

**Environment File Verification**:
```bash
# Check .env.example exists and has all required variables
cat .env.example | grep -E "DATABASE_URL|VAULT_PATH|API_HOST"

# Verify .env is in .gitignore
git check-ignore .env
# Should output: .env
```

**Completion Criteria**:
- [ ] Python virtual environment active and all packages import successfully
- [ ] Both Rust projects compile without errors or warnings
- [ ] cargo run executes successfully for both CLI and sync-service
- [ ] Environment variables documented and example file provided
- [ ] Setup instructions tested on a clean environment (or documented as tested)
