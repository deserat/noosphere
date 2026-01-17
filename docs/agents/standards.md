# Coding Standards

This document defines coding standards and conventions for the Noosphere project. All code should follow these guidelines to ensure consistency, maintainability, and quality.

## General Principles

### Code Quality

- **Readability over Cleverness**: Write code that's easy to understand
- **DRY (Don't Repeat Yourself)**: Extract common patterns
- **YAGNI (You Aren't Gonna Need It)**: Don't add unused features
- **Fail Fast**: Validate inputs early, clear error messages
- **Test Coverage**: Aim for 80%+ test coverage on critical paths

### Documentation

- **Docstrings/Comments**: Explain WHY, not WHAT (code shows what)
- **Type Hints**: Use type annotations extensively
- **README Files**: Each service has setup and usage docs
- **API Documentation**: Auto-generated from code (OpenAPI, rustdoc)

## Python Standards

### Style Guide

**Base**: Follow PEP 8 with modifications below.

**Line Length**: 100 characters (not 79)

**Imports**:
```python
# Standard library
import os
from pathlib import Path

# Third-party
from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, Integer, String

# Local application
from app.core.config import get_config
from app.models.item import Item
```

**Naming Conventions**:
```python
# Constants
MAX_RETRY_ATTEMPTS = 3
DATABASE_URL = "postgresql://..."

# Classes
class ItemService:
    pass

# Functions and methods
def classify_item(text: str) -> dict:
    pass

# Variables
user_id = "123"
is_active = True

# Private members
_internal_cache = {}
```

### Type Hints

**Always use type hints** for function signatures:

```python
from typing import List, Optional, Dict, Any
from datetime import datetime

def get_items(
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Item]:
    """Get items with optional filtering."""
    pass

async def classify_item(
    item: Item,
    model: str = "gemini-1.5-flash"
) -> Dict[str, Any]:
    """Classify item using AI model."""
    pass
```

### FastAPI Patterns

**Router Organization**:
```python
# app/api/endpoints/items.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.item import ItemCreate, ItemResponse
from app.crud.item import item_crud

router = APIRouter()

@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db)
) -> ItemResponse:
    """Create new item."""
    return item_crud.create(db, obj_in=item_in)
```

**Dependency Injection**:
```python
from fastapi import Depends

# Database session dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuration dependency
def get_current_config() -> Config:
    return get_config()

# Usage in endpoint
@router.get("/items")
async def list_items(
    db: Session = Depends(get_db),
    config: Config = Depends(get_current_config)
):
    pass
```

### SQLAlchemy Models

**Model Definition**:
```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector

from app.db.base import Base

class Item(Base):
    __tablename__ = "items"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Required fields
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)

    # Optional fields
    tags = Column(ARRAY(String), default=list)
    embedding = Column(Vector(768))

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Item(id={self.id}, title={self.title})>"
```

### Pydantic Schemas

**Request/Response Models**:
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import uuid

class ItemBase(BaseModel):
    """Base item schema."""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    category: str = Field(..., regex="^[a-z]+$")
    tags: List[str] = Field(default_factory=list)

class ItemCreate(ItemBase):
    """Item creation schema."""
    pass

class ItemUpdate(BaseModel):
    """Item update schema (all fields optional)."""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class ItemResponse(ItemBase):
    """Item response schema."""
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2
```

### Error Handling

**Custom Exceptions**:
```python
from fastapi import HTTPException, status

class ItemNotFoundError(HTTPException):
    def __init__(self, item_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )

# Usage
if not item:
    raise ItemNotFoundError(item_id)
```

**Validation Errors**:
```python
from pydantic import validator

class ItemCreate(BaseModel):
    title: str
    category: str

    @validator("category")
    def validate_category(cls, v):
        allowed = ["ideas", "tasks", "notes", "resources", "journal"]
        if v not in allowed:
            raise ValueError(f"Category must be one of {allowed}")
        return v
```

### Testing (pytest)

**Test Structure**:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import get_db
from app.models.item import Item

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Database session fixture."""
    # Create test database session
    yield session
    # Cleanup

def test_create_item(client: TestClient):
    """Test item creation endpoint."""
    response = client.post(
        "/api/items",
        json={"title": "Test", "content": "Content", "category": "ideas"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
    assert "id" in data
```

### Logging

**Standard Format**:
```python
import logging

logger = logging.getLogger(__name__)

# Usage
logger.info("Processing item", extra={"item_id": item.id})
logger.error("Classification failed", exc_info=True)
```

## Rust Standards

### Style Guide

**Base**: Follow Rust standard conventions (`cargo fmt`).

**Naming Conventions**:
```rust
// Constants
const MAX_RETRY_ATTEMPTS: u32 = 3;
const API_TIMEOUT_MS: u64 = 5000;

// Structs
struct AppState {
    selected_index: usize,
    items: Vec<Item>,
}

// Enums
enum ViewMode {
    List,
    Detail,
    Search,
}

// Functions
fn handle_key_event(app: &mut App, key: KeyEvent) -> Result<()> {
    // ...
}

// Modules
mod components;
mod api;
```

### Error Handling

**Use Result and anyhow**:
```rust
use anyhow::{Context, Result};

fn load_config(path: &str) -> Result<Config> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read config: {}", path))?;

    let config: Config = serde_yaml::from_str(&content)
        .with_context(|| "Failed to parse YAML")?;

    Ok(config)
}
```

**Custom Errors with thiserror**:
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("API request failed: {0}")]
    ApiError(String),

    #[error("File not found: {path}")]
    FileNotFound { path: String },

    #[error("Invalid configuration: {reason}")]
    ConfigError { reason: String },
}
```

### Elm Architecture (CLI)

**Model (app.rs)**:
```rust
/// Application state (Model in Elm Architecture)
pub struct App {
    /// Current view mode
    pub view: ViewMode,

    /// Selected item index
    pub selected_index: usize,

    /// List of items
    pub items: Vec<Item>,

    /// Input buffer for text entry
    pub input_buffer: String,

    /// Should quit flag
    pub should_quit: bool,
}

impl App {
    pub fn new() -> Self {
        Self {
            view: ViewMode::List,
            selected_index: 0,
            items: Vec::new(),
            input_buffer: String::new(),
            should_quit: false,
        }
    }
}
```

**Update (handler.rs)**:
```rust
use crossterm::event::{KeyCode, KeyEvent};
use anyhow::Result;

/// Handle key events (Update in Elm Architecture)
pub fn handle_key_event(app: &mut App, key: KeyEvent) -> Result<()> {
    match key.code {
        KeyCode::Char('q') => app.should_quit = true,
        KeyCode::Char('c') => app.view = ViewMode::Create,
        KeyCode::Down => {
            if app.selected_index < app.items.len() - 1 {
                app.selected_index += 1;
            }
        }
        KeyCode::Up => {
            if app.selected_index > 0 {
                app.selected_index -= 1;
            }
        }
        KeyCode::Enter => handle_enter(app)?,
        _ => {}
    }
    Ok(())
}
```

**View (ui.rs)**:
```rust
use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout},
    widgets::{Block, Borders, List, ListItem, Paragraph},
};

/// Render application (View in Elm Architecture)
pub fn render(app: &App, frame: &mut Frame) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),  // Header
            Constraint::Min(0),     // Content
            Constraint::Length(1),  // Status
        ])
        .split(frame.size());

    render_header(app, frame, chunks[0]);
    render_content(app, frame, chunks[1]);
    render_status(app, frame, chunks[2]);
}
```

**Event Loop (main.rs)**:
```rust
use crossterm::event::{self, Event};
use anyhow::Result;

fn main() -> Result<()> {
    let mut app = App::new();
    let mut terminal = setup_terminal()?;

    loop {
        // Render (View)
        terminal.draw(|f| ui::render(&app, f))?;

        // Poll event
        if let Event::Key(key) = event::read()? {
            // Update (based on event)
            handler::handle_key_event(&mut app, key)?;
        }

        // Check quit condition
        if app.should_quit {
            break;
        }
    }

    cleanup_terminal(&mut terminal)?;
    Ok(())
}
```

### Async Patterns (Sync Service)

**tokio Runtime**:
```rust
#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Load configuration
    let config = Config::load("config.yaml")?;

    // Start file watcher
    let (tx, rx) = mpsc::channel(100);
    tokio::spawn(watch_vault(config.clone(), tx));

    // Process events
    while let Some(event) = rx.recv().await {
        handle_vault_event(&config, event).await?;
    }

    Ok(())
}
```

**Error Handling in Async**:
```rust
async fn sync_item(api_client: &ApiClient, item: &Item) -> Result<()> {
    api_client
        .create_item(item)
        .await
        .with_context(|| format!("Failed to sync item: {}", item.title))?;

    Ok(())
}
```

### API Client

**reqwest Patterns**:
```rust
use reqwest::{Client, Response};
use serde::{Deserialize, Serialize};

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

    pub async fn create_item(&self, item: &ItemCreate) -> Result<Item> {
        let url = format!("{}/api/items", self.base_url);

        let response = self.client
            .post(&url)
            .json(item)
            .send()
            .await
            .with_context(|| "Failed to send request")?;

        if !response.status().is_success() {
            let status = response.status();
            let text = response.text().await?;
            anyhow::bail!("API error {}: {}", status, text);
        }

        let item = response.json::<Item>().await
            .with_context(|| "Failed to parse response")?;

        Ok(item)
    }
}
```

### Testing (cargo test)

**Unit Tests**:
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_initialization() {
        let app = App::new();
        assert_eq!(app.selected_index, 0);
        assert_eq!(app.items.len(), 0);
        assert!(!app.should_quit);
    }

    #[test]
    fn test_handle_quit_key() {
        let mut app = App::new();
        let key = KeyEvent::from(KeyCode::Char('q'));

        handle_key_event(&mut app, key).unwrap();

        assert!(app.should_quit);
    }
}
```

**Integration Tests** (`tests/integration_test.rs`):
```rust
use noosphere_cli::App;

#[test]
fn test_full_workflow() {
    let mut app = App::new();

    // Simulate user creating item
    app.input_buffer = "Test idea".to_string();
    handle_create(&mut app).unwrap();

    assert_eq!(app.items.len(), 1);
    assert_eq!(app.items[0].title, "Test idea");
}
```

### Logging (tracing)

**Setup**:
```rust
use tracing::{info, warn, error};

fn main() {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    info!("Application started");
}
```

**Usage**:
```rust
use tracing::{info, warn, error, instrument};

#[instrument]
async fn sync_item(item: &Item) -> Result<()> {
    info!(item_id = %item.id, "Starting sync");

    match api_client.create_item(item).await {
        Ok(_) => {
            info!(item_id = %item.id, "Sync successful");
            Ok(())
        }
        Err(e) => {
            error!(item_id = %item.id, error = %e, "Sync failed");
            Err(e)
        }
    }
}
```

## Git Workflow

**Branching Model**: This project uses **Git-Flow** for branch management.

### Git-Flow Overview

Git-Flow is a branching model that provides a robust framework for managing larger projects:

```
main (production-ready code, tagged releases)
  │
  └─── develop (integration branch for features)
        │
        ├─── feature/EPIC-1-1-repository-structure
        ├─── feature/EPIC-2-1-database-setup
        ├─── feature/add-authentication
        │
        ├─── release/v0.1.0 (release preparation)
        │
        └─── hotfix/critical-security-fix (emergency production fixes)
```

### Branch Types

**main**:
- Production-ready code only
- Tagged with version numbers (v0.1.0, v1.0.0, etc.)
- Protected branch (no direct commits)
- Merge only from `release/*` or `hotfix/*` branches

**develop**:
- Integration branch for features
- Always contains latest delivered development changes
- Base branch for all feature development
- Protected branch (requires PR review)

**feature/***:
- Branched from: `develop`
- Merge back to: `develop`
- Naming: `feature/EPIC-X-Y-description` or `feature/short-description`
- Deleted after merge

**release/***:
- Branched from: `develop`
- Merge to: `main` AND `develop`
- Naming: `release/vX.Y.Z`
- For release preparation (version bumps, final testing)

**hotfix/***:
- Branched from: `main`
- Merge to: `main` AND `develop`
- Naming: `hotfix/critical-issue-description`
- For emergency production fixes only

### Branch Naming Conventions

```bash
# Features (from develop)
feature/EPIC-1-1-repository-structure
feature/EPIC-2-1-database-setup
feature/add-user-authentication
feature/implement-search

# Releases (from develop)
release/v0.1.0
release/v1.0.0
release/v1.1.0

# Hotfixes (from main)
hotfix/security-vulnerability-fix
hotfix/critical-database-error

# Supporting branches
bugfix/fix-sync-race-condition    # Non-critical bugs (from develop)
docs/update-setup-guide            # Documentation only (from develop)
refactor/api-error-handling        # Refactoring (from develop)
```

### Git-Flow Commands

**Starting a Feature**:
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/EPIC-1-2-dev-environments
```

**Finishing a Feature**:
```bash
# Merge feature back to develop
git checkout develop
git pull origin develop
git merge --no-ff feature/EPIC-1-2-dev-environments
git push origin develop
git branch -d feature/EPIC-1-2-dev-environments
```

**Starting a Release**:
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v0.1.0

# Bump version, update changelog
# Run final tests
```

**Finishing a Release**:
```bash
# Merge to main (production)
git checkout main
git pull origin main
git merge --no-ff release/v0.1.0
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge --no-ff release/v0.1.0
git push origin develop

# Delete release branch
git branch -d release/v0.1.0
```

**Hotfix Process**:
```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# Fix the issue, test

# Merge to main
git checkout main
git merge --no-ff hotfix/critical-security-fix
git tag -a v0.1.1 -m "Hotfix v0.1.1"
git push origin main --tags

# Merge to develop
git checkout develop
git merge --no-ff hotfix/critical-security-fix
git push origin develop

# Delete hotfix branch
git branch -d hotfix/critical-security-fix
```

### Commit Messages

**Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `docs`: Documentation
- `test`: Testing
- `chore`: Maintenance

**Examples**:
```
feat(api): add item classification endpoint

Implement POST /api/items/{id}/classify endpoint using litellm
for AI-powered classification. Supports Gemini, Claude, and GPT models.

Closes #42
```

```
fix(sync): prevent concurrent file writes

Add file locking mechanism to prevent race conditions when
sync service and manual edits occur simultaneously.

Fixes #67
```

### Pull Request Template

```markdown
## Description
[What does this PR do?]

## Related Stories
- EPIC-X-Y: [Story title]

## Changes
- [Change 1]
- [Change 2]

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

## Code Review Guidelines

### Review Checklist

**Functionality**:
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling appropriate

**Quality**:
- [ ] Follows coding standards
- [ ] No code duplication
- [ ] Clear and readable
- [ ] Appropriate abstractions

**Testing**:
- [ ] Tests cover main paths
- [ ] Tests are meaningful
- [ ] No flaky tests

**Documentation**:
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] README updated if needed

### Review Comments

**Constructive Feedback**:
```
❌ "This is wrong."
✅ "Consider using `match` here for exhaustive pattern matching. It prevents bugs if new variants are added."

❌ "Why didn't you use X?"
✅ "Have you considered using X? It might simplify this by removing the manual iteration."
```

## Performance Guidelines

### Python

**Database Queries**:
```python
# ❌ N+1 queries
items = db.query(Item).all()
for item in items:
    tags = db.query(Tag).filter(Tag.item_id == item.id).all()

# ✅ Eager loading
items = db.query(Item).options(joinedload(Item.tags)).all()
```

**Async Operations**:
```python
# ❌ Sequential
result1 = await call_api_1()
result2 = await call_api_2()

# ✅ Parallel
result1, result2 = await asyncio.gather(
    call_api_1(),
    call_api_2()
)
```

### Rust

**Ownership**:
```rust
// ❌ Unnecessary cloning
fn process_item(item: Item) -> Result<()> {
    let title = item.title.clone();
    // Use title...
}

// ✅ Borrowing
fn process_item(item: &Item) -> Result<()> {
    let title = &item.title;
    // Use title...
}
```

**Iterators**:
```rust
// ❌ Collecting unnecessarily
let sum: i32 = items.iter()
    .map(|i| i.value)
    .collect::<Vec<_>>()
    .iter()
    .sum();

// ✅ Direct iteration
let sum: i32 = items.iter()
    .map(|i| i.value)
    .sum();
```

## Security Guidelines

### Input Validation

**Always Validate**:
```python
# Pydantic automatically validates
class ItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    category: str = Field(..., regex="^[a-z]+$")
```

### SQL Injection Prevention

```python
# ✅ Use ORM or parameterized queries
items = db.query(Item).filter(Item.title == user_input).all()

# ❌ String concatenation
query = f"SELECT * FROM items WHERE title = '{user_input}'"
```

### Secret Management

```python
# ✅ Environment variables
api_key = os.getenv("GEMINI_API_KEY")

# ❌ Hardcoded secrets
api_key = "AIzaSyD..."
```

## Tools and Automation

### Python Tools

**Linting**: `ruff` (replaces flake8, pylint)
**Type Checking**: `mypy`
**Formatting**: `black` or `ruff format`
**Testing**: `pytest`

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Rust Tools

**Formatting**: `cargo fmt`
**Linting**: `cargo clippy`
**Testing**: `cargo test`
**Documentation**: `cargo doc`

**Pre-commit Hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Python
cd api-service
ruff check .
mypy .

# Rust
cd ../cli
cargo fmt --check
cargo clippy -- -D warnings
```

## Documentation Standards

### Python Docstrings

**Google Style**:
```python
def classify_item(item: Item, model: str = "gemini-1.5-flash") -> dict:
    """Classify item using AI model.

    Args:
        item: The item to classify.
        model: AI model identifier (default: gemini-1.5-flash).

    Returns:
        Dictionary containing classification results with keys:
        - category: Suggested category
        - tags: List of suggested tags
        - confidence: Classification confidence (0-1)

    Raises:
        APIError: If AI API call fails.
        ValueError: If model is not supported.

    Example:
        >>> item = Item(title="Build app", content="...")
        >>> result = classify_item(item)
        >>> print(result["category"])
        'tasks'
    """
    pass
```

### Rust Documentation

**rustdoc Style**:
```rust
/// Handles keyboard events and updates application state.
///
/// This implements the Update phase of the Elm Architecture,
/// translating user input into state transitions.
///
/// # Arguments
///
/// * `app` - Mutable reference to application state
/// * `key` - Key event from terminal
///
/// # Returns
///
/// * `Ok(())` if event handled successfully
/// * `Err` if event processing failed
///
/// # Example
///
/// ```
/// let mut app = App::new();
/// let key = KeyEvent::from(KeyCode::Char('q'));
/// handle_key_event(&mut app, key)?;
/// assert!(app.should_quit);
/// ```
pub fn handle_key_event(app: &mut App, key: KeyEvent) -> Result<()> {
    // ...
}
```

## Maintenance and Refactoring

### When to Refactor

- **Code Duplication**: Same logic in 3+ places
- **Complex Functions**: >50 lines or >3 levels of nesting
- **Poor Names**: Unclear variable/function names
- **Tight Coupling**: Hard to test or change independently

### Refactoring Safety

1. **Write Tests First**: Ensure behavior is captured
2. **Small Steps**: One change at a time
3. **Run Tests**: After each change
4. **Commit Often**: Easy to revert if needed

## Resources

- **Python**: [PEP 8](https://pep8.org), [FastAPI Docs](https://fastapi.tiangolo.com)
- **Rust**: [Rust Book](https://doc.rust-lang.org/book/), [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- **Testing**: [pytest Docs](https://docs.pytest.org), [Rust Testing Guide](https://doc.rust-lang.org/book/ch11-00-testing.html)
