# Noosphere Sync Service

Background daemon that synchronizes the file-based markdown vault (`~/noosphere-vault/`) with the PostgreSQL database via the API service.

## Overview

The sync service is responsible for:
- ✅ **File watching**: Detects changes to vault files using the `notify` crate
- ✅ **Markdown parsing**: Reads markdown files with YAML frontmatter
- ✅ **Database synchronization**: Syncs vault ↔ database via HTTP API
- ✅ **File locking**: Prevents concurrent write conflicts
- ✅ **Content hashing**: Detects actual content changes (SHA-256)

**Critical**: This service is the **ONLY** service that touches the vault filesystem. The Python API service never directly accesses vault files.

## Quick Start

### 1. Setup Configuration

```bash
# Copy example configuration
cp config.example.yaml config.yaml

# Edit with your settings
vim config.yaml
```

### 2. Run the Service

```bash
# Development mode
cargo run

# Production mode (release build)
cargo build --release
./target/release/noosphere-sync
```

## Configuration

The sync service uses YAML configuration files for all settings.

### Configuration File

Create `config.yaml` from the template:

```bash
cp config.example.yaml config.yaml
```

**Important**: `config.yaml` is .gitignored (not tracked). This file contains user-specific paths and should not be committed to version control.

### Configuration Sections

#### Vault Settings

```yaml
vault:
  path: ~/noosphere-vault  # Path to vault directory (~ expansion supported)
  watch_recursive: true    # Watch subdirectories
  debounce_ms: 500         # Wait after last change before syncing
```

**Options**:

- `path` (string): Path to noosphere vault directory
  - Supports `~` expansion (e.g., `~/noosphere-vault` → `/home/user/noosphere-vault`)
  - Default: `~/noosphere-vault`
  - Example: `/var/lib/noosphere/vault` (absolute path)

- `watch_recursive` (boolean): Watch subdirectories for changes
  - `true`: Watch all subdirectories (recommended for category folders)
  - `false`: Only watch top-level directory
  - Default: `true`

- `debounce_ms` (integer): Debounce delay in milliseconds
  - Wait this long after the last file change before triggering sync
  - Prevents rapid-fire syncs during bulk operations (e.g., git pull)
  - Range: `100-5000` ms
  - Default: `500` ms (development), `1000` ms (production recommended)

#### API Client Settings

```yaml
api:
  base_url: http://127.0.0.1:8000  # API service URL
  timeout_ms: 5000                  # Request timeout
  retry_attempts: 3                 # Retry count
  retry_delay_ms: 1000              # Delay between retries
```

**Options**:

- `base_url` (string): Base URL of api-service
  - Must include protocol (`http://` or `https://`)
  - No trailing slash
  - Default: `http://127.0.0.1:8000` (local development)
  - Production: Use HTTPS (e.g., `https://api.example.com`)

- `timeout_ms` (integer): Request timeout in milliseconds
  - How long to wait for API response before failing
  - Range: `1000-30000` ms (1-30 seconds)
  - Default: `5000` ms (5 seconds)

- `retry_attempts` (integer): Number of retry attempts on failure
  - If API request fails, retry this many times
  - Range: `0-10`
  - Default: `3`
  - Set to `0` to disable retries

- `retry_delay_ms` (integer): Delay between retries in milliseconds
  - Base delay for exponential backoff: `delay * 2^attempt`
  - Range: `100-10000` ms
  - Default: `1000` ms (1 second)

#### Sync Behavior

```yaml
sync:
  batch_size: 10           # Files per batch
  sync_interval_ms: 60000  # Periodic sync interval
  ignore_patterns:         # Patterns to ignore
    - "*.lock"
    - "*.tmp"
```

**Options**:

- `batch_size` (integer): Number of files to process per batch
  - Prevents overwhelming API with too many concurrent requests
  - Range: `1-100`
  - Default: `10` (development), `20` (production recommended)

- `sync_interval_ms` (integer): Periodic sync interval in milliseconds
  - Run full vault scan this often, even if no changes detected
  - Ensures consistency if file events are missed
  - Range: `10000-300000` ms (10 seconds to 5 minutes)
  - Default: `60000` ms (1 minute development), `300000` ms (5 minutes production)

- `ignore_patterns` (array of strings): File patterns to ignore
  - Uses glob pattern matching (`*` = wildcard, `?` = single char)
  - Files matching these patterns are not synced to database
  - Default patterns:
    - `*.lock`: File lock files
    - `*.tmp`: Temporary files
    - `.DS_Store`: macOS metadata
    - `.noosphere-metadata`: Internal vault metadata

#### Logging Settings

```yaml
logging:
  level: info                     # Log level
  format: text                    # Log format
  file: logs/sync-service.log     # Log file path
  max_size_mb: 10                 # Rotation size
  max_backups: 5                  # Backup count
```

**Options**:

- `level` (string): Log level
  - `trace`: Very detailed (debugging)
  - `debug`: Detailed information (development)
  - `info`: General information (default)
  - `warn`: Warnings only
  - `error`: Errors only
  - Default: `info` (development), `warn` (production recommended)

- `format` (string): Log output format
  - `text`: Human-readable format (good for terminals)
  - `json`: Structured JSON format (good for log aggregation)
  - Default: `text` (development), `json` (production recommended)

- `file` (string): Log file path
  - Where to write log output
  - Directory is created if it doesn't exist
  - Default: `logs/sync-service.log`

- `max_size_mb` (integer): Maximum log file size in megabytes
  - When log reaches this size, it's rotated
  - Old file renamed to `sync-service.log.1`, etc.
  - Range: `1-1000` MB
  - Default: `10` MB

- `max_backups` (integer): Number of rotated log files to keep
  - After rotation, keep this many backup files
  - Oldest files deleted when limit reached
  - Range: `1-50`
  - Default: `5` (keeps ~50MB total at 10MB per file)

### Development vs Production

**Development Defaults** (config.example.yaml):
```yaml
vault:
  debounce_ms: 500          # Fast response
logging:
  level: info               # Verbose logging
  format: text              # Human-readable
api:
  base_url: http://127.0.0.1:8000  # Local server
sync:
  sync_interval_ms: 60000   # Frequent syncs (1 minute)
```

**Production Recommendations**:
```yaml
vault:
  debounce_ms: 1000         # Reduce CPU usage
logging:
  level: warn               # Reduce log volume
  format: json              # Structured logs for aggregation
api:
  base_url: https://api.example.com  # HTTPS required
sync:
  sync_interval_ms: 300000  # Less frequent (5 minutes)
  batch_size: 20            # Larger batches for efficiency
```

## Validation Rules

### Required Fields
All configuration sections are required:
- `vault`
- `api`
- `sync`
- `logging`

### Value Ranges
- `vault.debounce_ms`: 100-5000 ms
- `api.timeout_ms`: 1000-30000 ms
- `api.retry_attempts`: 0-10
- `api.retry_delay_ms`: 100-10000 ms
- `sync.batch_size`: 1-100
- `sync.sync_interval_ms`: 10000-300000 ms
- `logging.max_size_mb`: 1-1000 MB
- `logging.max_backups`: 1-50

### Valid Values
- `logging.level`: `trace`, `debug`, `info`, `warn`, `error`
- `logging.format`: `text`, `json`
- `vault.watch_recursive`: `true`, `false`

## Architecture

### Service Responsibilities

**This Service DOES**:
- ✅ Watch vault directory for file changes (notify crate)
- ✅ Parse markdown files with YAML frontmatter
- ✅ Write markdown files to vault (atomic operations)
- ✅ Compute content hashes (SHA-256 for change detection)
- ✅ Implement file locking (prevent concurrent writes)
- ✅ Sync vault → database (POST/PUT/DELETE to API)
- ✅ Sync database → vault (write markdown files from API)

**This Service DOES NOT**:
- ❌ Provide user interface (CLI responsibility)
- ❌ Implement business logic (API service responsibility)
- ❌ Perform AI classification (API service responsibility)
- ❌ Store data in database (API service responsibility)

### Tech Stack

- **Runtime**: tokio 1.35 (async runtime)
- **File Watching**: notify 6.x (cross-platform file system events)
- **HTTP Client**: reqwest 0.11 (API communication with rustls)
- **Serialization**: serde, serde_yaml, serde_json
- **Hashing**: sha2 (SHA-256 content hashing)
- **Error Handling**: anyhow, thiserror
- **Logging**: tracing, tracing-subscriber (structured logging)

## Development

### Building

```bash
# Debug build (fast compile, slower runtime)
cargo build

# Release build (slower compile, optimized runtime)
cargo build --release
```

### Testing

```bash
# Run all tests
cargo test --all-features

# Run specific test
cargo test test_config_deserialization

# Run tests with output
cargo test -- --nocapture
```

### Code Quality

```bash
# Format code
cargo fmt

# Check formatting
cargo fmt --check

# Run clippy (lints)
cargo clippy --all-targets --all-features -- -D warnings

# Check without building
cargo check --all-targets --all-features
```

### Coverage

```bash
# Install cargo-llvm-cov (if not installed)
cargo install cargo-llvm-cov

# Generate coverage report
cargo llvm-cov --all-features --workspace --lcov --output-path lcov.info

# Generate HTML report
cargo llvm-cov --all-features --workspace --html

# View report
open target/llvm-cov/html/index.html
```

## Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/noosphere-sync.service`:

```ini
[Unit]
Description=Noosphere Sync Service
After=network.target

[Service]
Type=simple
User=noosphere
WorkingDirectory=/opt/noosphere/sync-service
ExecStart=/opt/noosphere/sync-service/noosphere-sync
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable noosphere-sync
sudo systemctl start noosphere-sync
sudo systemctl status noosphere-sync
```

### launchd Service (macOS)

Create `~/Library/LaunchAgents/com.noosphere.sync.plist`:

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
    <key>WorkingDirectory</key>
    <string>/Users/username/noosphere/sync-service</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.noosphere.sync.plist
launchctl start com.noosphere.sync
```

## Troubleshooting

### Configuration Errors

**Error**: `Failed to read config file: config.yaml`
- **Solution**: Create config.yaml from template:
  ```bash
  cp config.example.yaml config.yaml
  ```

**Error**: `Failed to parse YAML configuration`
- **Solution**: Check YAML syntax. Common issues:
  - Incorrect indentation (use spaces, not tabs)
  - Missing colons after field names
  - Unquoted special characters

### File Permission Errors

**Error**: `Permission denied` when accessing vault
- **Solution**: Ensure service has read/write access:
  ```bash
  chown -R user:group ~/noosphere-vault
  chmod -R 755 ~/noosphere-vault
  ```

### Lock Timeout Errors

**Error**: `Lock timeout: failed to acquire lock`
- **Solution**: Check for stale lock files:
  ```bash
  ls -la ~/noosphere-vault/.noosphere/locks/
  # Remove stale locks if process no longer running
  rm ~/noosphere-vault/.noosphere/locks/*.lock
  ```

### API Connection Errors

**Error**: `Connection refused`
- **Solution**: Ensure API service is running:
  ```bash
  # Check if API service is running
  curl http://127.0.0.1:8000/health

  # Verify api.base_url in config.yaml matches running service
  ```

## Security

### Configuration File Security

- **DO NOT commit** `config.yaml` to version control (contains user paths)
- `config.yaml` is automatically .gitignored
- Only `config.example.yaml` (template) is tracked in git
- API authentication tokens should be set via environment variables (see Issue #15)

### File System Access

- Service requires read/write access to vault directory
- Uses file locking to prevent concurrent write conflicts
- Lock files stored in `.noosphere/locks/` subdirectory

## Related Documentation

- [AGENTS.md](AGENTS.md) - Service context and boundaries
- [Vault Structure](../docs/vault-structure.md) - Markdown file format
- [Issue #12](https://github.com/deserat/noosphere/issues/12) - Vault utilities implementation
- [Issue #15](https://github.com/deserat/noosphere/issues/15) - Configuration loaders with env vars
- [Issue #17](https://github.com/deserat/noosphere/issues/17) - Sync service skeleton

## License

Part of the Noosphere project.
