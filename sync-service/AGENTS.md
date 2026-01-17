# Sync Service Context (Rust)

This file provides context for AI coding assistants working on the Noosphere sync service. It defines service boundaries, responsibilities, and file synchronization patterns.

## Service Overview

**Purpose**: File watching service that synchronizes markdown vault with PostgreSQL database via API.

**Technology Stack**:
- **File Watching**: notify 6.x (cross-platform file system events)
- **Async Runtime**: tokio 1.35 (async operations)
- **HTTP Client**: reqwest 0.11 (API communication)
- **Serialization**: serde, serde_json, serde_yaml (data formats)
- **Hashing**: sha2 (content change detection)
- **Error Handling**: anyhow, thiserror (error types)
- **Logging**: tracing, tracing-subscriber (structured logging)

**Deployment**: Background service/daemon

## Service Boundaries

### Responsibilities

**This Service DOES**:
- ✅ Watch file vault directory for changes (create, modify, delete)
- ✅ Parse markdown files with YAML frontmatter
- ✅ Detect content changes (SHA256 hashing)
- ✅ Sync vault → database (POST/PUT/DELETE to API)
- ✅ Sync database → vault (write markdown files)
- ✅ Handle file conflicts (last-write-wins)
- ✅ Implement file locking to prevent concurrent writes
- ✅ Debounce rapid file changes
- ✅ Run as background service

**This Service DOES NOT**:
- ❌ Provide user interface (CLI responsibility)
- ❌ Implement business logic (API service responsibility)
- ❌ Perform AI classification (API service responsibility)
- ❌ Store data in database (API service responsibility)
- ❌ Serve REST API endpoints (API service responsibility)

### Dependencies

**External Services**:
- API Service: `http://localhost:8000/api` (configurable)
- File Vault: `~/noosphere-vault` (configurable)

**Consumed By**:
- None (autonomous background service)

## Directory Structure

```
sync-service/
├── src/
│   ├── main.rs           # Service entry point
│   ├── config.rs         # Configuration management
│   ├── watcher.rs        # File system watching logic
│   ├── sync.rs           # Synchronization logic
│   ├── markdown.rs       # Markdown parsing/writing
│   ├── lock.rs           # File locking mechanism
│   ├── hash.rs           # Content hashing utilities
│   └── api.rs            # API client
├── tests/                # Integration tests
│   ├── watcher_tests.rs
│   └── sync_tests.rs
├── Cargo.toml           # Rust dependencies
└── .env                 # Environment variables (not committed)
```

## Synchronization Flow

### Vault → Database (File Changes)

```
File Created/Modified
    ↓
File System Event (notify)
    ↓
Debounce (500ms)
    ↓
Read Markdown File
    ↓
Parse YAML Frontmatter + Content
    ↓
Check SHA256 Hash (changed?)
    ↓
Acquire File Lock
    ↓
POST /api/items (create) OR PUT /api/items/{id} (update)
    ↓
API Returns Classification
    ↓
Update Frontmatter with Classification
    ↓
Release File Lock
```

### Database → Vault (API Updates)

```
API Update Event (webhook or polling)
    ↓
GET /api/items/{id}
    ↓
Check if File Exists
    ↓
Acquire File Lock
    ↓
Generate Markdown with Frontmatter
    ↓
Write to Vault File
    ↓
Update Hash Cache
    ↓
Release File Lock
```

### Conflict Resolution

**Last-Write-Wins Strategy**:
```
Concurrent Modification Detected
    ↓
Compare Timestamps (modified_at)
    ↓
Keep Newer Version
    ↓
Discard Older Version
    ↓
Log Warning
```

## File Vault Structure

### Directory Layout

```
~/noosphere-vault/
├── ideas/              # Category: Ideas
│   └── 2024-01-15-automation-dashboard.md
├── tasks/              # Category: Tasks
│   └── 2024-01-15-review-pr-42.md
├── notes/              # Category: Notes
│   └── 2024-01-15-meeting-notes.md
├── resources/          # Category: Resources
│   └── 2024-01-15-rust-tutorial.md
├── journal/            # Category: Journal
│   └── 2024-01-15-daily-log.md
└── .noosphere/         # Metadata directory
    ├── locks/          # File locks
    └── cache/          # Content hashes
```

### Markdown File Format

```markdown
---
id: 550e8400-e29b-41d4-a716-446655440000
title: Build home automation dashboard
category: ideas
tags:
  - automation
  - smart-home
created: 2024-01-15T10:00:00Z
updated: 2024-01-15T10:05:00Z
surfaced: 2024-01-15T10:00:00Z
next_surface: 2024-01-16T10:00:00Z
cadence: daily
---

# Build home automation dashboard

Need to build a centralized dashboard for controlling all smart home devices.
Should integrate with Home Assistant and provide:

- Real-time device status
- Automation rule editor
- Energy usage monitoring
- Voice control integration

Next steps:
1. Research existing dashboards
2. Design UI mockups
3. Choose tech stack
```

## File Watching

### Watcher Setup

```rust
use notify::{Config, Event, RecommendedWatcher, RecursiveMode, Watcher};
use std::path::Path;
use tokio::sync::mpsc;

pub async fn watch_vault(
    vault_path: &Path,
    tx: mpsc::Sender<FileEvent>,
) -> anyhow::Result<()> {
    let (watcher_tx, mut watcher_rx) = mpsc::channel(100);

    let mut watcher = RecommendedWatcher::new(
        move |res: Result<Event, _>| {
            if let Ok(event) = res {
                let _ = watcher_tx.blocking_send(event);
            }
        },
        Config::default(),
    )?;

    watcher.watch(vault_path, RecursiveMode::Recursive)?;

    // Process events
    while let Some(event) = watcher_rx.recv().await {
        process_file_event(event, &tx).await?;
    }

    Ok(())
}
```

### Event Processing

```rust
use notify::EventKind;

async fn process_file_event(
    event: Event,
    tx: &mpsc::Sender<FileEvent>,
) -> anyhow::Result<()> {
    match event.kind {
        EventKind::Create(_) => {
            for path in event.paths {
                if is_markdown_file(&path) {
                    tx.send(FileEvent::Created(path)).await?;
                }
            }
        }
        EventKind::Modify(_) => {
            for path in event.paths {
                if is_markdown_file(&path) {
                    tx.send(FileEvent::Modified(path)).await?;
                }
            }
        }
        EventKind::Remove(_) => {
            for path in event.paths {
                if is_markdown_file(&path) {
                    tx.send(FileEvent::Deleted(path)).await?;
                }
            }
        }
        _ => {}
    }

    Ok(())
}

fn is_markdown_file(path: &Path) -> bool {
    path.extension().map_or(false, |ext| ext == "md")
        && !path.starts_with(".noosphere")  // Ignore metadata directory
}
```

### Debouncing

```rust
use std::collections::HashMap;
use std::time::{Duration, Instant};
use tokio::time::sleep;

pub struct Debouncer {
    pending: HashMap<PathBuf, Instant>,
    delay: Duration,
}

impl Debouncer {
    pub fn new(delay_ms: u64) -> Self {
        Self {
            pending: HashMap::new(),
            delay: Duration::from_millis(delay_ms),
        }
    }

    pub async fn debounce(&mut self, path: PathBuf) -> bool {
        let now = Instant::now();

        if let Some(last_time) = self.pending.get(&path) {
            if now.duration_since(*last_time) < self.delay {
                // Too soon, update timestamp and skip
                self.pending.insert(path, now);
                return false;
            }
        }

        // Record event and wait
        self.pending.insert(path.clone(), now);
        sleep(self.delay).await;

        // Check if any newer events occurred
        if let Some(last_time) = self.pending.get(&path) {
            now.duration_since(*last_time) >= self.delay
        } else {
            false
        }
    }
}
```

## Markdown Processing

### Parsing

```rust
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Debug, Serialize, Deserialize)]
pub struct Frontmatter {
    pub id: String,
    pub title: String,
    pub category: String,
    pub tags: Vec<String>,
    pub created: String,
    pub updated: Option<String>,
    pub surfaced: Option<String>,
    pub next_surface: Option<String>,
    pub cadence: Option<String>,
}

pub fn parse_markdown(path: &Path) -> anyhow::Result<(Frontmatter, String)> {
    let content = fs::read_to_string(path)?;

    // Split frontmatter and body
    let parts: Vec<&str> = content.splitn(3, "---\n").collect();

    if parts.len() < 3 {
        anyhow::bail!("Invalid markdown format: missing frontmatter");
    }

    // Parse YAML frontmatter
    let frontmatter: Frontmatter = serde_yaml::from_str(parts[1])?;

    // Body content
    let body = parts[2].trim().to_string();

    Ok((frontmatter, body))
}
```

### Writing

```rust
pub fn write_markdown(
    path: &Path,
    frontmatter: &Frontmatter,
    content: &str,
) -> anyhow::Result<()> {
    let yaml = serde_yaml::to_string(frontmatter)?;

    let markdown = format!("---\n{}---\n\n{}", yaml, content);

    fs::write(path, markdown)?;

    Ok(())
}
```

## File Locking

### Lock Implementation

```rust
use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

pub struct FileLock {
    lock_file: PathBuf,
}

impl FileLock {
    pub fn new(file_path: &Path) -> Self {
        let lock_dir = file_path.parent().unwrap().join(".noosphere/locks");
        std::fs::create_dir_all(&lock_dir).ok();

        let lock_file = lock_dir.join(format!(
            "{}.lock",
            file_path.file_name().unwrap().to_string_lossy()
        ));

        Self { lock_file }
    }

    pub fn acquire(&self, timeout: Duration) -> anyhow::Result<LockGuard> {
        let start = SystemTime::now();

        loop {
            match OpenOptions::new()
                .write(true)
                .create_new(true)
                .open(&self.lock_file)
            {
                Ok(mut file) => {
                    // Write PID to lock file
                    write!(file, "{}", std::process::id())?;
                    return Ok(LockGuard {
                        lock_file: self.lock_file.clone(),
                    });
                }
                Err(e) if e.kind() == io::ErrorKind::AlreadyExists => {
                    // Check if stale lock
                    if self.is_stale_lock()? {
                        self.force_unlock()?;
                        continue;
                    }

                    // Wait and retry
                    if start.elapsed()? > timeout {
                        anyhow::bail!("Lock timeout");
                    }

                    std::thread::sleep(Duration::from_millis(100));
                }
                Err(e) => return Err(e.into()),
            }
        }
    }

    fn is_stale_lock(&self) -> anyhow::Result<bool> {
        let metadata = std::fs::metadata(&self.lock_file)?;
        let modified = metadata.modified()?;
        let age = SystemTime::now().duration_since(modified)?;

        // Consider lock stale if older than 5 minutes
        Ok(age > Duration::from_secs(300))
    }

    fn force_unlock(&self) -> anyhow::Result<()> {
        std::fs::remove_file(&self.lock_file)?;
        Ok(())
    }
}

pub struct LockGuard {
    lock_file: PathBuf,
}

impl Drop for LockGuard {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.lock_file);
    }
}
```

## Content Hashing

### Hash Calculation

```rust
use sha2::{Sha256, Digest};
use std::fs;
use std::path::Path;

pub fn calculate_file_hash(path: &Path) -> anyhow::Result<String> {
    let content = fs::read(path)?;
    let mut hasher = Sha256::new();
    hasher.update(&content);
    let result = hasher.finalize();

    Ok(format!("{:x}", result))
}

pub fn has_content_changed(path: &Path, cached_hash: Option<&str>) -> anyhow::Result<bool> {
    let current_hash = calculate_file_hash(path)?;

    match cached_hash {
        Some(cached) => Ok(current_hash != cached),
        None => Ok(true),  // No cached hash, assume changed
    }
}
```

### Hash Cache

```rust
use std::collections::HashMap;
use std::path::PathBuf;

pub struct HashCache {
    cache: HashMap<PathBuf, String>,
}

impl HashCache {
    pub fn new() -> Self {
        Self {
            cache: HashMap::new(),
        }
    }

    pub fn get(&self, path: &PathBuf) -> Option<&str> {
        self.cache.get(path).map(|s| s.as_str())
    }

    pub fn update(&mut self, path: PathBuf, hash: String) {
        self.cache.insert(path, hash);
    }

    pub fn remove(&mut self, path: &PathBuf) {
        self.cache.remove(path);
    }
}
```

## API Integration

### Sync Operations

```rust
use crate::api::ApiClient;
use crate::markdown::{Frontmatter, parse_markdown};
use std::path::Path;

pub async fn sync_file_to_api(
    api_client: &ApiClient,
    file_path: &Path,
) -> anyhow::Result<()> {
    let (frontmatter, content) = parse_markdown(file_path)?;

    // Check if item exists
    if let Ok(existing) = api_client.get_item(&frontmatter.id).await {
        // Update existing item
        api_client.update_item(&frontmatter.id, &frontmatter, &content).await?;
    } else {
        // Create new item
        api_client.create_item(&frontmatter, &content).await?;
    }

    Ok(())
}

pub async fn sync_api_to_file(
    api_client: &ApiClient,
    item_id: &str,
    vault_path: &Path,
) -> anyhow::Result<()> {
    let item = api_client.get_item(item_id).await?;

    let file_path = vault_path
        .join(&item.category)
        .join(format!("{}.md", item.title.replace(' ', "-").to_lowercase()));

    // Create directory if needed
    if let Some(parent) = file_path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    // Write markdown file
    write_markdown(&file_path, &item.frontmatter, &item.content)?;

    Ok(())
}
```

## Configuration

### Environment Variables

```bash
# Vault path
VAULT_PATH=~/noosphere-vault

# API service URL
API_BASE_URL=http://localhost:8000

# Sync settings
SYNC_INTERVAL_MS=60000        # 1 minute
DEBOUNCE_MS=500               # 500ms debounce

# Logging
RUST_LOG=info
```

### Configuration File

```rust
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Config {
    pub vault: VaultConfig,
    pub api: ApiConfig,
    pub sync: SyncConfig,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct VaultConfig {
    pub path: PathBuf,
    pub watch_recursive: bool,
    pub debounce_ms: u64,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ApiConfig {
    pub base_url: String,
    pub timeout_ms: u64,
    pub retry_attempts: u32,
    pub retry_delay_ms: u64,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct SyncConfig {
    pub batch_size: usize,
    pub sync_interval_ms: u64,
    pub ignore_patterns: Vec<String>,
}
```

## Error Handling

### Retry Logic

```rust
use tokio::time::{sleep, Duration};

pub async fn retry_with_backoff<F, Fut, T>(
    mut f: F,
    max_attempts: u32,
    base_delay_ms: u64,
) -> anyhow::Result<T>
where
    F: FnMut() -> Fut,
    Fut: std::future::Future<Output = anyhow::Result<T>>,
{
    let mut attempts = 0;

    loop {
        match f().await {
            Ok(result) => return Ok(result),
            Err(e) => {
                attempts += 1;

                if attempts >= max_attempts {
                    return Err(e);
                }

                let delay = base_delay_ms * 2u64.pow(attempts - 1);
                tracing::warn!(
                    error = %e,
                    attempt = attempts,
                    delay_ms = delay,
                    "Operation failed, retrying"
                );

                sleep(Duration::from_millis(delay)).await;
            }
        }
    }
}
```

## Logging

### Structured Logging

```rust
use tracing::{info, warn, error, debug};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .with_target(false)
        .init();

    info!("Sync service starting");

    // ...
}

// Usage
info!(file = ?path, "File created");
warn!(file = ?path, error = %e, "Failed to sync file");
error!(item_id = %id, "API request failed");
debug!(hash = %hash, "Content hash calculated");
```

## Testing

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_markdown() {
        let content = r#"---
id: test-id
title: Test
category: ideas
tags: []
created: 2024-01-15T10:00:00Z
---

# Test

Content here
"#;

        let (frontmatter, body) = parse_markdown_content(content).unwrap();
        assert_eq!(frontmatter.id, "test-id");
        assert_eq!(frontmatter.title, "Test");
        assert!(body.contains("Content here"));
    }
}
```

### Integration Tests

```rust
#[tokio::test]
async fn test_file_sync_workflow() {
    // Create test file
    let temp_dir = tempfile::tempdir().unwrap();
    let file_path = temp_dir.path().join("test.md");

    // Write markdown
    let frontmatter = Frontmatter { /* ... */ };
    write_markdown(&file_path, &frontmatter, "Test content").unwrap();

    // Sync to API (mocked)
    // ...

    // Verify API call made
    // ...
}
```

## Git Workflow (Git-Flow)

**This project uses Git-Flow branching model.**

**Development Process**:
```bash
# Start new feature from develop
git checkout develop
git pull origin develop
git checkout -b feature/sync-file-locking

# Make changes, commit regularly
git add .
git commit -m "feat(sync): implement file locking mechanism"

# Keep feature branch updated
git checkout develop
git pull origin develop
git checkout feature/sync-file-locking
git merge develop

# When complete, merge back to develop (via PR)
git checkout develop
git pull origin develop
git merge --no-ff feature/sync-file-locking
git push origin develop
git branch -d feature/sync-file-locking
```

**Branch Types**:
- `main` - Production releases only (tagged)
- `develop` - Integration branch (base for features)
- `feature/*` - Feature development (from develop)
- `release/*` - Release preparation (from develop)
- `hotfix/*` - Emergency fixes (from main)

See [`docs/agents/standards.md`](../docs/agents/standards.md#git-workflow) for complete git-flow documentation.

## Deployment

### Systemd Service (Linux)

```ini
[Unit]
Description=Noosphere Sync Service
After=network.target

[Service]
Type=simple
User=noosphere
Environment="VAULT_PATH=/home/noosphere/noosphere-vault"
Environment="API_BASE_URL=http://localhost:8000"
ExecStart=/usr/local/bin/noosphere-sync
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### launchd Service (macOS)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.noosphere.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/noosphere-sync</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>VAULT_PATH</key>
        <string>/Users/username/noosphere-vault</string>
        <key>API_BASE_URL</key>
        <string>http://localhost:8000</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

## Troubleshooting

### File Permission Errors

```
Error: Permission denied
Fix: Ensure service has read/write access to vault directory
     chown -R user:group ~/noosphere-vault
```

### Lock Timeout Errors

```
Error: Lock timeout
Fix: Check for stale lock files in .noosphere/locks/
     Remove if process no longer running
```

### API Connection Errors

```
Error: Connection refused
Fix: Ensure API service is running
     Check API_BASE_URL is correct
```

## Performance Considerations

- **Debouncing**: Prevent rapid file change storms
- **Batching**: Batch multiple changes together
- **Async I/O**: Non-blocking file operations
- **Selective Watching**: Ignore hidden files, lock files

## Resources

- [notify Documentation](https://docs.rs/notify)
- [tokio Documentation](https://tokio.rs)
- [File Locking Patterns](https://en.wikipedia.org/wiki/File_locking)

## Next Steps

When working on this service:

1. Read [`docs/agents/architecture.md`](../docs/agents/architecture.md) for system architecture
2. Read [`docs/agents/standards.md`](../docs/agents/standards.md) for Rust coding standards
3. Check [`docs/project/stories/EPIC-5-2-sync-service-scaffolding.md`](../docs/project/stories/EPIC-5-2-sync-service-scaffolding.md)
4. Focus on Phase 1 setup first (basic file watching), then Phase 2 sync logic
