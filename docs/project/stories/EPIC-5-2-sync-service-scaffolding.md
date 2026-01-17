# Rust Sync Service with File Watching

**Epic**: Service Scaffolding
**Priority**: P1
**Story Points**: 8

## User Story

As a developer,
I need a minimal but functional Rust file-watching service that monitors the vault and syncs changes to the API,
So that I can verify the sync architecture and file watching capabilities.

## Acceptance Criteria

### Rust Project Setup
- [ ] `sync-service/Cargo.toml` created with dependencies:
  ```toml
  [package]
  name = "noosphere-sync"
  version = "0.1.0"
  edition = "2021"

  [dependencies]
  tokio = { version = "1.35", features = ["full"] }
  notify = "6.1"
  reqwest = { version = "0.11", features = ["json"] }
  serde = { version = "1.0", features = ["derive"] }
  serde_yaml = "0.9"
  serde_json = "1.0"
  anyhow = "1.0"
  thiserror = "1.0"
  tracing = "0.1"
  tracing-subscriber = { version = "0.3", features = ["env-filter"] }
  shellexpand = "3.1"
  sha2 = "0.10"
  chrono = "0.4"

  [[bin]]
  name = "noosphere-sync"
  path = "src/main.rs"
  ```

### Main Application
- [ ] `sync-service/src/main.rs` created with service initialization:
  ```rust
  use anyhow::Result;
  use tracing::{info, error};
  use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

  mod config;
  mod watcher;
  mod sync;
  mod api;

  #[tokio::main]
  async fn main() -> Result<()> {
      // Initialize logging
      tracing_subscriber::registry()
          .with(tracing_subscriber::EnvFilter::new(
              std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
          ))
          .with(tracing_subscriber::fmt::layer())
          .init();

      info!("Starting Noosphere Sync Service v0.1.0");

      // Load configuration
      let config = config::Config::load("config.yaml")?;
      info!("Configuration loaded successfully");

      // Verify vault directory exists
      if !config.vault.path.exists() {
          error!("Vault directory does not exist: {:?}", config.vault.path);
          anyhow::bail!("Vault directory not found");
      }
      info!("Vault directory verified: {:?}", config.vault.path);

      // Verify API connection
      if let Err(e) = api::check_health(&config.api.base_url).await {
          error!("API health check failed: {}", e);
          anyhow::bail!("Cannot connect to API service");
      }
      info!("API connection verified");

      // Start file watcher
      info!("Starting file watcher...");
      watcher::watch_vault(&config).await?;

      Ok(())
  }
  ```

### Configuration Module (Reference)
- [ ] Configuration module already defined in EPIC-4-2
- [ ] Verify `sync-service/src/config.rs` exists and matches specification

### File Watcher Module
- [ ] `sync-service/src/watcher.rs` created with file watching logic:
  ```rust
  use notify::{
      Config, Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher,
  };
  use std::path::PathBuf;
  use std::time::Duration;
  use tokio::sync::mpsc;
  use tracing::{info, warn, error, debug};
  use anyhow::Result;

  use crate::config;
  use crate::sync::SyncEngine;

  pub async fn watch_vault(config: &config::Config) -> Result<()> {
      let (tx, mut rx) = mpsc::channel(100);

      // Create debouncer to avoid excessive sync on rapid changes
      let debounce_duration = Duration::from_millis(config.vault.debounce_ms);

      // Create watcher
      let mut watcher = RecommendedWatcher::new(
          move |res: Result<Event, notify::Error>| {
              if let Ok(event) = res {
                  let _ = tx.blocking_send(event);
              }
          },
          Config::default().with_poll_interval(Duration::from_secs(1)),
      )?;

      // Watch vault directory
      let watch_mode = if config.vault.watch_recursive {
          RecursiveMode::Recursive
      } else {
          RecursiveMode::NonRecursive
      };

      watcher.watch(&config.vault.path, watch_mode)?;
      info!("File watcher started for {:?}", config.vault.path);

      // Create sync engine
      let sync_engine = SyncEngine::new(config.clone());

      // Process file events
      let mut last_event_time = std::time::Instant::now();
      let mut pending_changes: Vec<PathBuf> = Vec::new();

      loop {
          tokio::select! {
              Some(event) = rx.recv() => {
                  if should_ignore_event(&event, &config.sync.ignore_patterns) {
                      debug!("Ignoring event: {:?}", event);
                      continue;
                  }

                  match event.kind {
                      EventKind::Create(_) | EventKind::Modify(_) | EventKind::Remove(_) => {
                          for path in event.paths {
                              debug!("File changed: {:?}", path);
                              pending_changes.push(path);
                          }
                          last_event_time = std::time::Instant::now();
                      }
                      _ => {}
                  }
              }

              _ = tokio::time::sleep(debounce_duration) => {
                  if !pending_changes.is_empty()
                      && last_event_time.elapsed() >= debounce_duration
                  {
                      info!("Processing {} file changes", pending_changes.len());

                      // Sync changes to API
                      if let Err(e) = sync_engine.sync_files(&pending_changes).await {
                          error!("Sync failed: {}", e);
                      } else {
                          info!("Sync completed successfully");
                      }

                      pending_changes.clear();
                  }
              }
          }
      }
  }

  fn should_ignore_event(event: &Event, ignore_patterns: &[String]) -> bool {
      for path in &event.paths {
          let path_str = path.to_string_lossy();
          for pattern in ignore_patterns {
              if path_str.contains(pattern) {
                  return true;
              }
          }
      }
      false
  }
  ```

### Sync Engine Module
- [ ] `sync-service/src/sync.rs` created with placeholder sync logic:
  ```rust
  use std::path::PathBuf;
  use anyhow::Result;
  use tracing::{info, warn};

  use crate::config::Config;
  use crate::api;

  pub struct SyncEngine {
      config: Config,
  }

  impl SyncEngine {
      pub fn new(config: Config) -> Self {
          Self { config }
      }

      pub async fn sync_files(&self, paths: &[PathBuf]) -> Result<()> {
          info!("Syncing {} files to API", paths.len());

          for path in paths {
              if let Err(e) = self.sync_file(path).await {
                  warn!("Failed to sync {:?}: {}", path, e);
              }
          }

          Ok(())
      }

      async fn sync_file(&self, path: &PathBuf) -> Result<()> {
          // TODO: Implement actual sync logic
          // 1. Read file content
          // 2. Parse frontmatter
          // 3. Compute content hash
          // 4. Send to API (create or update)
          // 5. Handle API response

          info!("Syncing file: {:?}", path);

          // Placeholder: Just log the file path
          // Real implementation in Phase 2

          Ok(())
      }
  }
  ```

### API Client Module
- [ ] `sync-service/src/api.rs` created with API client:
  ```rust
  use anyhow::Result;
  use reqwest::Client;
  use serde::{Deserialize, Serialize};
  use tracing::{info, error};

  #[derive(Debug, Deserialize)]
  struct HealthResponse {
      status: String,
  }

  pub async fn check_health(base_url: &str) -> Result<()> {
      let client = Client::new();
      let url = format!("{}/api/health", base_url);

      info!("Checking API health at {}", url);

      let response = client
          .get(&url)
          .timeout(std::time::Duration::from_secs(5))
          .send()
          .await?;

      if !response.status().is_success() {
          anyhow::bail!("API health check returned status: {}", response.status());
      }

      let health: HealthResponse = response.json().await?;

      if health.status != "healthy" {
          anyhow::bail!("API reported unhealthy status: {}", health.status);
      }

      info!("API health check passed");
      Ok(())
  }

  // Placeholder for future API methods
  pub async fn create_item(/* parameters */) -> Result<()> {
      // TODO: Implement in Phase 2
      Ok(())
  }

  pub async fn update_item(/* parameters */) -> Result<()> {
      // TODO: Implement in Phase 2
      Ok(())
  }
  ```

### Service Startup Script
- [ ] `sync-service/run.sh` created for development:
  ```bash
  #!/bin/bash
  set -e

  echo "Starting Noosphere Sync Service..."

  # Build project
  echo "Building Rust project..."
  cargo build --release

  # Run service
  echo "Starting sync service..."
  RUST_LOG=info cargo run --release
  ```
- [ ] Script made executable: `chmod +x sync-service/run.sh`

### Service Verification
- [ ] Service builds successfully: `cargo build`
- [ ] Service starts successfully: `./run.sh`
- [ ] File watcher monitors vault directory
- [ ] API health check succeeds at startup
- [ ] File changes trigger debounced events
- [ ] Service shuts down gracefully (Ctrl+C)

## Technical Notes

**notify Crate**:
- Cross-platform file system watcher
- Uses native OS APIs (inotify on Linux, FSEvents on macOS, ReadDirectoryChangesW on Windows)
- Supports recursive and non-recursive watching
- Debouncing prevents excessive sync on rapid changes

**Async Runtime (Tokio)**:
- `tokio::main` macro for async main function
- `tokio::select!` for concurrent event processing
- File watcher runs in background thread, sends events via channel

**Debouncing Strategy**:
- Wait `debounce_ms` after last change before syncing
- Prevents excessive API calls during file saves
- Accumulates changes and syncs in batch
- Example: 500ms debounce means sync happens 500ms after last file change

**File Event Filtering**:
- Ignore patterns from config.yaml (*.lock, *.tmp, .DS_Store)
- Only process Create, Modify, Remove events
- Ignore metadata-only changes (access time, etc.)

**Sync Engine Design**:
- Phase 1: Placeholder that logs file paths
- Phase 2: Read markdown, parse frontmatter, sync to API
- Phase 3: Conflict resolution, bidirectional sync

**API Client Design**:
- reqwest for HTTP client (async, feature-rich)
- Health check on startup (fail fast if API unavailable)
- Timeout and retry logic for resilience
- JSON serialization via serde

**Error Handling**:
- Fail fast at startup (config, vault path, API connection)
- Log and continue at runtime (individual file sync errors don't crash service)
- Graceful shutdown on Ctrl+C or SIGTERM

**Development vs Production**:
```bash
# Development
RUST_LOG=debug cargo run

# Production
RUST_LOG=info cargo run --release
```

**Placeholder Implementation**:
- File watcher works and detects changes
- Sync engine logs but doesn't actually sync
- API client has health check only
- Full implementation in Phase 2 (AI Classification)

## Dependencies

- **Blocks**:
  - Phase 2 stories (Sync service must exist for file-based capture)
- **Blocked By**:
  - EPIC-1-3 (Rust environment needed)
  - EPIC-3-1 (Vault structure needed for watching)
  - EPIC-4-2 (Configuration module needed)
  - EPIC-5-1 (API service needed for health check)
- **Related**:
  - EPIC-5-3 (Startup script will launch both services)

## Verification

### Service Build Test
```bash
cd sync-service

# Build project
cargo build

# Expected output:
#    Compiling noosphere-sync v0.1.0 (/path/to/sync-service)
#     Finished dev [unoptimized + debuginfo] target(s) in 30.00s

# Verify binary created
ls -lh target/debug/noosphere-sync
```

### Service Startup Test
```bash
# Ensure API service is running first
cd ../api-service
./run.sh &

# Start sync service
cd ../sync-service
./run.sh

# Expected output:
# Starting Noosphere Sync Service...
# Building Rust project...
#     Finished release [optimized] target(s) in 0.50s
# Starting sync service...
# 2024-01-15T10:00:00.000Z  INFO noosphere_sync: Starting Noosphere Sync Service v0.1.0
# 2024-01-15T10:00:00.001Z  INFO noosphere_sync: Configuration loaded successfully
# 2024-01-15T10:00:00.002Z  INFO noosphere_sync: Vault directory verified: "/home/user/noosphere-vault"
# 2024-01-15T10:00:00.003Z  INFO noosphere_sync::api: Checking API health at http://127.0.0.1:8000/api/health
# 2024-01-15T10:00:00.050Z  INFO noosphere_sync::api: API health check passed
# 2024-01-15T10:00:00.051Z  INFO noosphere_sync: Starting file watcher...
# 2024-01-15T10:00:00.052Z  INFO noosphere_sync::watcher: File watcher started for "/home/user/noosphere-vault"
```

### File Watching Test
```bash
# With sync service running, create a test file
echo "# Test Note" > ~/noosphere-vault/Inbox/test.md

# Expected sync service log output:
# 2024-01-15T10:01:00.000Z DEBUG noosphere_sync::watcher: File changed: "/home/user/noosphere-vault/Inbox/test.md"
# 2024-01-15T10:01:00.500Z  INFO noosphere_sync::watcher: Processing 1 file changes
# 2024-01-15T10:01:00.501Z  INFO noosphere_sync::sync: Syncing 1 files to API
# 2024-01-15T10:01:00.502Z  INFO noosphere_sync::sync: Syncing file: "/home/user/noosphere-vault/Inbox/test.md"
# 2024-01-15T10:01:00.503Z  INFO noosphere_sync::watcher: Sync completed successfully

# Modify the file
echo "Updated content" >> ~/noosphere-vault/Inbox/test.md

# Should see another sync after debounce period

# Delete the file
rm ~/noosphere-vault/Inbox/test.md

# Should see deletion event logged
```

### Ignore Patterns Test
```bash
# Create a lock file (should be ignored)
touch ~/noosphere-vault/Inbox/test.md.lock

# Expected: No sync event (ignored by pattern)

# Create a temp file (should be ignored)
touch ~/noosphere-vault/Inbox/test.tmp

# Expected: No sync event (ignored by pattern)

# Create a normal file
touch ~/noosphere-vault/Inbox/real-note.md

# Expected: Sync event triggered after debounce
```

### API Health Check Test
```bash
# Stop API service
pkill -f "python.*src.main"

# Try to start sync service
./run.sh

# Expected error:
# 2024-01-15T10:00:00.000Z ERROR noosphere_sync: API health check failed: ...
# Error: Cannot connect to API service

# Restart API service
cd ../api-service
./run.sh &

# Retry sync service (should succeed)
cd ../sync-service
./run.sh
```

### Graceful Shutdown Test
```bash
# Start sync service
./run.sh

# Press Ctrl+C

# Expected output:
# ^C
# 2024-01-15T10:00:00.000Z  INFO noosphere_sync: Shutting down...

# Verify clean shutdown (no panic, no error messages)
```

**Completion Criteria**:
- [ ] Rust project builds successfully with all dependencies
- [ ] Service starts and loads configuration
- [ ] Vault directory verification at startup
- [ ] API health check succeeds at startup
- [ ] File watcher monitors vault directory (recursive)
- [ ] File changes trigger debounced sync events
- [ ] Ignore patterns filter out unwanted files
- [ ] Placeholder sync engine logs file changes
- [ ] Service shuts down gracefully without panics
- [ ] Logging configured and working (tracing crate)
