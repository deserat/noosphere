# CLI Service Context (Rust/ratatui)

This file provides context for AI coding assistants working on the Noosphere CLI. It defines service boundaries, responsibilities, patterns, and the Elm Architecture implementation.

## Service Overview

**Purpose**: Terminal user interface (TUI) for frictionless capture and interaction with the Noosphere knowledge system.

**Technology Stack**:
- **TUI Framework**: ratatui 0.26 (Elm Architecture pattern)
- **Terminal**: crossterm 0.27 (cross-platform terminal manipulation)
- **Async Runtime**: tokio 1.35 (async operations)
- **HTTP Client**: reqwest 0.11 (API communication)
- **CLI Args**: clap 4.4 (argument parsing)
- **Serialization**: serde, serde_json (JSON handling)
- **Error Handling**: anyhow, thiserror (error types)
- **Logging**: tracing, tracing-subscriber (structured logging)

**Architecture Pattern**: Elm Architecture (Model-Update-View)

## Service Boundaries

### Responsibilities

**This Service DOES**:
- ✅ Provide terminal-based UI for item capture and browsing
- ✅ Sub-second capture time (frictionless entry)
- ✅ Communicate with API service via REST endpoints
- ✅ Display surfaced items in interactive TUI
- ✅ Handle keyboard navigation and shortcuts
- ✅ Store JWT tokens securely (OS keyring, Phase 2+)
- ✅ Provide search interface

**This Service DOES NOT**:
- ❌ Implement business logic (API service responsibility)
- ❌ Watch file system (sync-service responsibility)
- ❌ Store data locally (API/database responsibility)
- ❌ Perform AI classification (API service responsibility)
- ❌ Directly manipulate markdown files (sync-service handles vault)

### Dependencies

**External Services**:
- API Service: `http://localhost:8000/api` (configurable)

**Consumed By**:
- End users via terminal

## Directory Structure

```
cli/
├── src/
│   ├── main.rs            # Application entry point, event loop
│   ├── app.rs             # Model: Application state
│   ├── ui.rs              # View: Rendering logic
│   ├── handler.rs         # Update: Event handlers
│   ├── event.rs           # Event types and polling
│   ├── tui.rs             # Terminal setup/teardown
│   ├── components/        # Reusable UI components
│   │   ├── mod.rs
│   │   ├── item_list.rs   # Item list widget
│   │   ├── item_detail.rs # Item detail view
│   │   ├── input.rs       # Input field component
│   │   └── header.rs      # Header/status bar
│   └── api/               # API client module
│       ├── mod.rs
│       ├── client.rs      # HTTP client wrapper
│       ├── items.rs       # Item endpoints
│       └── types.rs       # API response types
├── tests/                 # Integration tests
│   ├── ui_tests.rs
│   └── api_tests.rs
├── Cargo.toml            # Rust dependencies
└── .env                  # Environment variables (not committed)
```

## Elm Architecture Pattern

### Overview

The CLI follows the **Elm Architecture** for predictable state management:

```
┌─────────────────────────────────────────┐
│          Event Loop (main.rs)            │
│                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────┐│
│  │  Poll    │──▶│  Update  │──▶│ View ││
│  │  Events  │   │  State   │   │(Render)││
│  └──────────┘   └──────────┘   └──────┘│
│       ▲              │              │    │
│       │              ▼              ▼    │
│       │         ┌────────┐    ┌────────┐│
│       └─────────│  App   │◀───│Terminal││
│                 │ (Model)│    │        ││
│                 └────────┘    └────────┘│
└─────────────────────────────────────────┘
```

**Key Principles**:
- **Model**: Single source of truth (App struct)
- **Update**: Pure functions (event → state change)
- **View**: Pure rendering (state → UI)
- **Event Loop**: Poll → Update → View → Repeat

### Model (app.rs)

Application state lives in the `App` struct:

```rust
pub struct App {
    /// Current view mode
    pub view: ViewMode,

    /// Selected item index in list
    pub selected_index: usize,

    /// List of items fetched from API
    pub items: Vec<Item>,

    /// Currently displayed item (detail view)
    pub current_item: Option<Item>,

    /// Input buffer for capture/search
    pub input_buffer: String,

    /// Input mode (normal, capture, search)
    pub input_mode: InputMode,

    /// Should quit application
    pub should_quit: bool,

    /// API client
    pub api_client: ApiClient,

    /// Status message
    pub status_message: Option<String>,
}

pub enum ViewMode {
    List,       // Item list view
    Detail,     // Single item detail
    Capture,    // Quick capture interface
    Search,     // Search interface
    Settings,   // Settings view
}

pub enum InputMode {
    Normal,     // Navigation mode
    Editing,    // Text input mode
}
```

### Update (handler.rs)

Event handlers modify state based on input:

```rust
use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};
use anyhow::Result;

/// Main event handler (Update in Elm Architecture)
pub fn handle_key_event(app: &mut App, key: KeyEvent) -> Result<()> {
    match app.input_mode {
        InputMode::Normal => handle_normal_mode(app, key),
        InputMode::Editing => handle_editing_mode(app, key),
    }
}

fn handle_normal_mode(app: &mut App, key: KeyEvent) -> Result<()> {
    match key.code {
        KeyCode::Char('q') => app.should_quit = true,
        KeyCode::Char('c') => {
            app.view = ViewMode::Capture;
            app.input_mode = InputMode::Editing;
        }
        KeyCode::Char('/') => {
            app.view = ViewMode::Search;
            app.input_mode = InputMode::Editing;
        }
        KeyCode::Down | KeyCode::Char('j') => {
            if app.selected_index < app.items.len() - 1 {
                app.selected_index += 1;
            }
        }
        KeyCode::Up | KeyCode::Char('k') => {
            if app.selected_index > 0 {
                app.selected_index -= 1;
            }
        }
        KeyCode::Enter => handle_enter(app)?,
        _ => {}
    }
    Ok(())
}

fn handle_editing_mode(app: &mut App, key: KeyEvent) -> Result<()> {
    match key.code {
        KeyCode::Esc => {
            app.input_mode = InputMode::Normal;
            app.input_buffer.clear();
        }
        KeyCode::Enter => handle_submit(app)?,
        KeyCode::Char(c) => {
            app.input_buffer.push(c);
        }
        KeyCode::Backspace => {
            app.input_buffer.pop();
        }
        _ => {}
    }
    Ok(())
}
```

### View (ui.rs)

Rendering logic transforms state into terminal UI:

```rust
use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout},
    widgets::{Block, Borders, List, ListItem, Paragraph},
    style::{Color, Modifier, Style},
};

/// Main render function (View in Elm Architecture)
pub fn render(app: &App, frame: &mut Frame) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),  // Header
            Constraint::Min(0),     // Content
            Constraint::Length(3),  // Status/Input
        ])
        .split(frame.size());

    render_header(app, frame, chunks[0]);

    match app.view {
        ViewMode::List => render_item_list(app, frame, chunks[1]),
        ViewMode::Detail => render_item_detail(app, frame, chunks[1]),
        ViewMode::Capture => render_capture_view(app, frame, chunks[1]),
        ViewMode::Search => render_search_view(app, frame, chunks[1]),
        ViewMode::Settings => render_settings_view(app, frame, chunks[1]),
    }

    render_status_bar(app, frame, chunks[2]);
}

fn render_item_list(app: &App, frame: &mut Frame, area: Rect) {
    let items: Vec<ListItem> = app
        .items
        .iter()
        .enumerate()
        .map(|(i, item)| {
            let style = if i == app.selected_index {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default()
            };

            ListItem::new(format!("{} - {}", item.category, item.title))
                .style(style)
        })
        .collect();

    let list = List::new(items)
        .block(Block::default().title("Items").borders(Borders::ALL));

    frame.render_widget(list, area);
}
```

### Event Loop (main.rs)

Main loop: Poll → Update → Render:

```rust
use crossterm::event::{self, Event};
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    // Setup terminal
    let mut terminal = setup_terminal()?;

    // Initialize application state
    let mut app = App::new();

    // Fetch initial items from API
    app.items = app.api_client.list_items(None, 50, 0).await?;

    // Event loop
    loop {
        // View: Render current state
        terminal.draw(|f| ui::render(&app, f))?;

        // Poll: Wait for events
        if let Event::Key(key) = event::read()? {
            // Update: Modify state based on event
            handler::handle_key_event(&mut app, key)?;
        }

        // Check quit condition
        if app.should_quit {
            break;
        }
    }

    // Cleanup terminal
    cleanup_terminal(&mut terminal)?;
    Ok(())
}
```

## API Integration

### API Client

```rust
use reqwest::{Client, Response};
use serde::{Deserialize, Serialize};
use anyhow::Result;

pub struct ApiClient {
    base_url: String,
    client: Client,
}

impl ApiClient {
    pub fn new(base_url: String) -> Self {
        Self {
            base_url,
            client: Client::new(),
        }
    }

    pub async fn list_items(
        &self,
        category: Option<&str>,
        limit: usize,
        offset: usize,
    ) -> Result<Vec<Item>> {
        let mut url = format!("{}/api/items?limit={}&offset={}", self.base_url, limit, offset);

        if let Some(cat) = category {
            url.push_str(&format!("&category={}", cat));
        }

        let response = self.client.get(&url).send().await?;
        response.error_for_status()?.json().await.map_err(Into::into)
    }

    pub async fn create_item(&self, item: &ItemCreate) -> Result<Item> {
        let url = format!("{}/api/items", self.base_url);

        let response = self.client
            .post(&url)
            .json(item)
            .send()
            .await?;

        response.error_for_status()?.json().await.map_err(Into::into)
    }

    pub async fn search_items(&self, query: &str) -> Result<Vec<Item>> {
        let url = format!("{}/api/items/search?query={}", self.base_url, query);

        let response = self.client.get(&url).send().await?;
        response.error_for_status()?.json().await.map_err(Into::into)
    }
}
```

### Data Types

```rust
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {
    pub id: String,
    pub title: String,
    pub content: String,
    pub category: String,
    pub tags: Vec<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Serialize)]
pub struct ItemCreate {
    pub title: String,
    pub content: String,
    pub category: String,
    pub tags: Vec<String>,
}
```

## User Interface

### Views

**List View** (default):
```
┌─────────────────────────────────────────┐
│ Noosphere - Second Brain         q:quit │
├─────────────────────────────────────────┤
│ ideas - Build home automation dashboard │
│ tasks - Review PR #42                   │
│ notes - Meeting notes 2024-01-15        │
│                                          │
│                                          │
├─────────────────────────────────────────┤
│ c:capture /:search j/k:nav Enter:detail │
└─────────────────────────────────────────┘
```

**Capture View**:
```
┌─────────────────────────────────────────┐
│ Quick Capture                   Esc:back│
├─────────────────────────────────────────┤
│                                          │
│ ┌─────────────────────────────────────┐ │
│ │ Type your idea here...              │ │
│ │ _                                   │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ Enter to save, Esc to cancel            │
│                                          │
├─────────────────────────────────────────┤
│ AI will classify and tag automatically  │
└─────────────────────────────────────────┘
```

**Detail View**:
```
┌─────────────────────────────────────────┐
│ Item Detail                     Esc:back│
├─────────────────────────────────────────┤
│ Title: Build home automation dashboard  │
│ Category: ideas                          │
│ Tags: [automation, smart-home]           │
│ Created: 2024-01-15 10:00:00            │
│                                          │
│ ─────────────────────────────────────── │
│                                          │
│ Need to build a centralized dashboard   │
│ for controlling all smart home devices. │
│ Should integrate with Home Assistant.   │
│                                          │
├─────────────────────────────────────────┤
│ e:edit d:delete                         │
└─────────────────────────────────────────┘
```

### Keyboard Shortcuts

**Global**:
- `q`: Quit application
- `c`: Quick capture
- `/`: Search
- `?`: Help

**List View**:
- `j` / `↓`: Move down
- `k` / `↑`: Move up
- `Enter`: View details
- `e`: Edit selected item
- `d`: Delete selected item

**Capture/Search**:
- `Esc`: Cancel
- `Enter`: Submit
- `Backspace`: Delete character

## Configuration

### Environment Variables

```bash
# API service URL
API_BASE_URL=http://localhost:8000

# Log level
RUST_LOG=info
```

### Configuration File (Future)

```yaml
# ~/.config/noosphere/cli.yaml
api:
  base_url: http://localhost:8000
  timeout_ms: 5000
  retry_attempts: 3

ui:
  theme: dark
  show_timestamps: true
  items_per_page: 20

keybindings:
  quit: q
  capture: c
  search: /
```

## Testing

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_initialization() {
        let app = App::new();
        assert_eq!(app.selected_index, 0);
        assert_eq!(app.view, ViewMode::List);
        assert!(!app.should_quit);
    }

    #[test]
    fn test_navigation_down() {
        let mut app = App::new();
        app.items = vec![
            Item { /* ... */ },
            Item { /* ... */ },
        ];

        let key = KeyEvent::from(KeyCode::Down);
        handle_key_event(&mut app, key).unwrap();

        assert_eq!(app.selected_index, 1);
    }
}
```

### Integration Tests

```rust
#[tokio::test]
async fn test_capture_workflow() {
    let mut app = App::new();

    // Start capture
    handle_key_event(&mut app, KeyEvent::from(KeyCode::Char('c'))).unwrap();
    assert_eq!(app.view, ViewMode::Capture);
    assert_eq!(app.input_mode, InputMode::Editing);

    // Type content
    for c in "Test idea".chars() {
        handle_key_event(&mut app, KeyEvent::from(KeyCode::Char(c))).unwrap();
    }
    assert_eq!(app.input_buffer, "Test idea");

    // Submit (mocked API call)
    // ... test API integration
}
```

## Development Workflow

### Running Locally

```bash
cd cli

# Run in development mode
cargo run

# Run with logging
RUST_LOG=debug cargo run

# Run tests
cargo test

# Check for errors
cargo check

# Format code
cargo fmt

# Lint
cargo clippy
```

### Building Release

```bash
# Build optimized binary
cargo build --release

# Binary location
./target/release/noosphere

# Install to system
cargo install --path .
```

### Git Workflow (Git-Flow)

**This project uses Git-Flow branching model.**

**Development Process**:
```bash
# Start new feature from develop
git checkout develop
git pull origin develop
git checkout -b feature/cli-capture-interface

# Make changes, commit regularly
git add .
git commit -m "feat(cli): add quick capture view"

# Keep feature branch updated
git checkout develop
git pull origin develop
git checkout feature/cli-capture-interface
git merge develop

# When complete, merge back to develop (via PR)
git checkout develop
git pull origin develop
git merge --no-ff feature/cli-capture-interface
git push origin develop
git branch -d feature/cli-capture-interface
```

**Branch Types**:
- `main` - Production releases only (tagged)
- `develop` - Integration branch (base for features)
- `feature/*` - Feature development (from develop)
- `release/*` - Release preparation (from develop)
- `hotfix/*` - Emergency fixes (from main)

See [`docs/agents/standards.md`](../docs/agents/standards.md#git-workflow) for complete git-flow documentation.

## Common Patterns

### Async Operations

```rust
// Spawn async task for API call
tokio::spawn(async move {
    match api_client.create_item(&item).await {
        Ok(created) => {
            // Update UI with result
        }
        Err(e) => {
            // Show error message
        }
    }
});
```

### Error Display

```rust
fn show_error(app: &mut App, error: &anyhow::Error) {
    app.status_message = Some(format!("Error: {}", error));
}
```

### Debouncing Input

```rust
use tokio::time::{sleep, Duration};

async fn debounced_search(app: &mut App, query: String) {
    sleep(Duration::from_millis(300)).await;

    // Only search if query hasn't changed
    if app.input_buffer == query {
        let results = app.api_client.search_items(&query).await.unwrap();
        app.items = results;
    }
}
```

## Performance Considerations

- **Lazy Loading**: Fetch items on-demand, pagination
- **Debouncing**: Wait for user to stop typing before searching
- **Async Operations**: Don't block UI during API calls
- **Efficient Rendering**: Only re-render changed portions (ratatui handles this)

## Troubleshooting

### API Connection Errors

```
Error: Connection refused
Fix: Ensure API service is running at http://localhost:8000
     Check API_BASE_URL environment variable
```

### Terminal Rendering Issues

```
Error: Broken UI after crash
Fix: Reset terminal with `reset` command
     Ensure cleanup_terminal() is called on exit
```

## Resources

- [ratatui Documentation](https://ratatui.rs)
- [Elm Architecture Guide](https://guide.elm-lang.org/architecture/)
- [crossterm Documentation](https://docs.rs/crossterm)
- [tokio Documentation](https://tokio.rs)

## Next Steps

When working on this service:

1. Read [`docs/agents/architecture.md`](../docs/agents/architecture.md) for system architecture
2. Read [`docs/agents/standards.md`](../docs/agents/standards.md) for Rust coding standards
3. Check [`docs/project/stories/`](../docs/project/stories/) for current user stories
4. Focus on Phase 1 setup (EPIC-1-2) then Phase 2 capture interface
