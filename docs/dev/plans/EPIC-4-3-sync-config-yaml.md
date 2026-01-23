# EPIC-4-3: YAML Configuration System - Sync Service

## Issue Reference
- **GitHub Issue**: #23
- **Epic**: EPIC-4 - Configuration Management
- **Priority**: P1
- **Story Points**: 2
- **Service**: sync-service (Rust)

## Feature Summary

Create a YAML-based configuration system for sync-service to manage vault watching, API client settings, sync behavior, and logging configuration without modifying code.

## Implementation Plan

### Current State Analysis
- **Existing**: serde_yaml 0.9, serde with derive features already in Cargo.toml (from Issue #12)
- **Existing**: src/vault/ module with parser, writer, template, lock, hash utilities
- **Missing**: config.rs module, config.example.yaml file, documentation

### Files to Create

1. **sync-service/src/config.rs** - Configuration module
   - Config struct (main container)
   - VaultConfig: path, watch_recursive, debounce_ms
   - ApiConfig: base_url, timeout_ms, retry_attempts, retry_delay_ms
   - SyncConfig: batch_size, sync_interval_ms, ignore_patterns
   - LoggingConfig: level, format, file, max_size_mb, max_backups
   - impl Config::load(path) method using serde_yaml
   - Unit tests in #[cfg(test)] module

2. **sync-service/config.example.yaml** - Configuration template
   - All configuration sections with defaults
   - Comprehensive inline comments explaining each option
   - Development-oriented defaults (localhost, verbose logging)
   - Security notes about environment variables

3. **sync-service/tests/config_test.rs** - Integration tests
   - Test loading config.example.yaml
   - Verify all fields deserialize correctly

### Files to Modify

1. **sync-service/Cargo.toml**
   - Add shellexpand = "3.1" for tilde (~) expansion in paths

2. **sync-service/src/lib.rs**
   - Add: `pub mod config;`

3. **sync-service/.gitignore** (create if not exists)
   - Add: `config.yaml` (user-specific, not tracked)
   - Add: `!config.example.yaml` (template, tracked)
   - Explanation: Prevents committing user-specific paths/settings

4. **sync-service/README.md** (update or create)
   - Configuration section with all options documented
   - Development vs production recommendations
   - Setup instructions (copy config.example.yaml to config.yaml)
   - Field descriptions and valid value ranges

## Architecture Decisions

### Why serde_yaml?
- Already in dependencies (added in Issue #12)
- Standard YAML parser for Rust ecosystem
- Integrates seamlessly with serde derive macros
- Supports complex nested structures

### Why shellexpand?
- Industry standard for shell-style path expansion
- Handles `~` → `$HOME` expansion correctly
- Cross-platform (Unix and Windows)
- Minimal dependency (~5KB)

### Why PathBuf for file paths?
- Type-safe path handling
- Works seamlessly with std::fs operations
- serde can deserialize String → PathBuf automatically
- Cross-platform path handling

### Configuration Loading Strategy
- **Phase 1 (this issue)**: Simple YAML file loading
- **Phase 2 (Issue #15)**: Add environment variable overrides
- **Phase 3 (Issue #15)**: Add validation and defaults
- Keep it minimal and focused for now

## Configuration Structure

### VaultConfig
```rust
pub struct VaultConfig {
    pub path: PathBuf,           // ~/noosphere-vault
    pub watch_recursive: bool,   // Watch subdirectories
    pub debounce_ms: u64,        // Debounce delay (500ms)
}
```

### ApiConfig
```rust
pub struct ApiConfig {
    pub base_url: String,        // http://127.0.0.1:8000
    pub timeout_ms: u64,         // Request timeout (5000ms)
    pub retry_attempts: u32,     // Number of retries (3)
    pub retry_delay_ms: u64,     // Delay between retries (1000ms)
}
```

### SyncConfig
```rust
pub struct SyncConfig {
    pub batch_size: usize,           // Files per batch (10)
    pub sync_interval_ms: u64,       // Periodic sync (60000ms)
    pub ignore_patterns: Vec<String>, // Skip these files
}
```

### LoggingConfig
```rust
pub struct LoggingConfig {
    pub level: String,           // info, debug, warn, error, trace
    pub format: String,          // text or json
    pub file: PathBuf,           // logs/sync-service.log
    pub max_size_mb: u64,        // Log rotation size (10MB)
    pub max_backups: u32,        // Number of backup files (5)
}
```

## Configuration Defaults (Development-Oriented)

```yaml
# Vault Configuration
vault:
  path: ~/noosphere-vault      # User's home directory
  watch_recursive: true         # Watch subdirectories
  debounce_ms: 500              # Wait 500ms after last change

# API Client Configuration
api:
  base_url: http://127.0.0.1:8000  # Local development server
  timeout_ms: 5000                  # 5 second request timeout
  retry_attempts: 3                 # Retry failed requests 3 times
  retry_delay_ms: 1000              # 1 second between retries

# Sync Behavior Configuration
sync:
  batch_size: 10                    # Process 10 files per batch
  sync_interval_ms: 60000           # Sync every 60 seconds
  ignore_patterns:                  # Skip these file patterns
    - "*.lock"                      # Lock files
    - "*.tmp"                       # Temporary files
    - ".DS_Store"                   # macOS metadata
    - ".noosphere-metadata"         # Internal metadata

# Logging Configuration
logging:
  level: info                       # info, debug, warn, error, trace
  format: text                      # text (human-readable) or json
  file: logs/sync-service.log       # Log file path
  max_size_mb: 10                   # Rotate at 10MB
  max_backups: 5                    # Keep 5 backup files
```

## Implementation Steps

1. **Add shellexpand dependency**
   ```bash
   cd sync-service
   cargo add shellexpand
   ```

2. **Create src/config.rs** with configuration structs
   - Define all four config structs with #[derive(Debug, Clone, Deserialize, Serialize)]
   - Implement Config::load(path) method
   - Add unit tests for deserialization

3. **Expose config module** in src/lib.rs
   - Add: `pub mod config;`

4. **Create config.example.yaml** with comprehensive comments
   - All sections with default values
   - Inline comments explaining each field
   - Development vs production notes

5. **Update .gitignore** to exclude user config
   - Add config.yaml (not tracked)
   - Add !config.example.yaml (tracked)

6. **Update README.md** with configuration documentation
   - Configuration section
   - All options explained with valid ranges
   - Setup instructions
   - Development vs production recommendations

7. **Create tests/config_test.rs** integration test
   - Test loading config.example.yaml
   - Verify all fields populated correctly

8. **Run quality checks**
   ```bash
   cargo fmt
   cargo clippy --all-targets --all-features -- -D warnings
   cargo test --all-features
   ```

## Testing Strategy

### Unit Tests (in src/config.rs)
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_deserialization() {
        let yaml = r#"
vault:
  path: ~/test-vault
  watch_recursive: true
  debounce_ms: 500
api:
  base_url: http://localhost:8000
  timeout_ms: 5000
  retry_attempts: 3
  retry_delay_ms: 1000
sync:
  batch_size: 10
  sync_interval_ms: 60000
  ignore_patterns:
    - "*.lock"
logging:
  level: info
  format: text
  file: logs/test.log
  max_size_mb: 10
  max_backups: 5
"#;

        let config: Config = serde_yaml::from_str(yaml).unwrap();
        assert_eq!(config.vault.debounce_ms, 500);
        assert_eq!(config.api.retry_attempts, 3);
        assert_eq!(config.sync.batch_size, 10);
        assert_eq!(config.logging.level, "info");
    }

    #[test]
    fn test_path_buf_parsing() {
        let yaml = r#"
vault:
  path: ~/test-vault
  watch_recursive: true
  debounce_ms: 500
api:
  base_url: http://localhost:8000
  timeout_ms: 5000
  retry_attempts: 3
  retry_delay_ms: 1000
sync:
  batch_size: 10
  sync_interval_ms: 60000
  ignore_patterns: []
logging:
  level: info
  format: text
  file: logs/test.log
  max_size_mb: 10
  max_backups: 5
"#;

        let config: Config = serde_yaml::from_str(yaml).unwrap();
        assert!(config.vault.path.to_string_lossy().contains("test-vault"));
    }
}
```

### Integration Test (tests/config_test.rs)
```rust
use noosphere_sync::config::Config;

#[test]
fn test_load_example_config() {
    let config = Config::load("config.example.yaml")
        .expect("Failed to load config.example.yaml");

    // Verify vault config
    assert!(!config.vault.path.as_os_str().is_empty());
    assert_eq!(config.vault.watch_recursive, true);
    assert_eq!(config.vault.debounce_ms, 500);

    // Verify API config
    assert_eq!(config.api.base_url, "http://127.0.0.1:8000");
    assert_eq!(config.api.timeout_ms, 5000);
    assert_eq!(config.api.retry_attempts, 3);

    // Verify sync config
    assert_eq!(config.sync.batch_size, 10);
    assert_eq!(config.sync.sync_interval_ms, 60000);
    assert!(!config.sync.ignore_patterns.is_empty());

    // Verify logging config
    assert_eq!(config.logging.level, "info");
    assert_eq!(config.logging.format, "text");
}
```

**Coverage target**: 80%+ (standard for Rust configuration code)

## Verification

### Manual Verification Steps
```bash
cd sync-service

# 1. Check dependencies added
cat Cargo.toml | grep shellexpand
# Should show: shellexpand = "3.1"

# 2. Format check
cargo fmt --check
# Should pass with no changes needed

# 3. Lint check (all warnings as errors)
cargo clippy --all-targets --all-features -- -D warnings
# Should pass with no warnings

# 4. Run all tests
cargo test --all-features
# All tests should pass

# 5. Test loading config example
cargo run --example validate_config config.example.yaml
# Should successfully parse and display all config values

# 6. Verify gitignore works
cp config.example.yaml config.yaml
git status
# Should NOT show config.yaml in untracked files
# Should show config.example.yaml as tracked

# 7. Check documentation
cat README.md | grep -A 20 "Configuration"
# Should show comprehensive configuration documentation
```

## Documentation Requirements

### README.md Configuration Section

```markdown
## Configuration

The sync service uses YAML configuration files for all settings.

### Setup

1. Copy the example configuration:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. Edit `config.yaml` with your settings:
   ```bash
   vim config.yaml
   ```

### Configuration Options

#### Vault Settings

- `vault.path`: Path to noosphere vault directory (supports ~ expansion)
  - Default: `~/noosphere-vault`
  - Example: `/home/user/Documents/vault`

- `vault.watch_recursive`: Watch subdirectories for changes
  - Default: `true`
  - Set to `false` for flat directory structure

- `vault.debounce_ms`: Milliseconds to wait after file change before syncing
  - Default: `500`
  - Range: 100-5000
  - Lower = more responsive, higher = less CPU usage

#### API Client Settings

- `api.base_url`: Base URL of api-service
  - Default: `http://127.0.0.1:8000`
  - Production: Use HTTPS with proper domain

- `api.timeout_ms`: Request timeout in milliseconds
  - Default: `5000`
  - Range: 1000-30000

- `api.retry_attempts`: Number of retry attempts on failure
  - Default: `3`
  - Range: 0-10

- `api.retry_delay_ms`: Delay between retries
  - Default: `1000`
  - Range: 100-10000

#### Sync Behavior

- `sync.batch_size`: Number of files to process per batch
  - Default: `10`
  - Range: 1-100

- `sync.sync_interval_ms`: Periodic sync interval
  - Default: `60000` (1 minute)
  - Range: 10000-300000

- `sync.ignore_patterns`: File patterns to ignore
  - Default: `["*.lock", "*.tmp", ".DS_Store", ".noosphere-metadata"]`
  - Supports glob patterns

#### Logging Settings

- `logging.level`: Log level
  - Default: `info`
  - Options: `trace`, `debug`, `info`, `warn`, `error`

- `logging.format`: Log output format
  - Default: `text`
  - Options: `text` (human-readable), `json` (structured)

- `logging.file`: Log file path
  - Default: `logs/sync-service.log`

- `logging.max_size_mb`: Log rotation size in megabytes
  - Default: `10`

- `logging.max_backups`: Number of rotated log files to keep
  - Default: `5`

### Development vs Production

**Development** (config.example.yaml defaults):
- `vault.debounce_ms: 500` - Fast response for development
- `logging.level: info` - Verbose logging for debugging
- `api.base_url: http://127.0.0.1:8000` - Local API server

**Production** (recommended):
- `vault.debounce_ms: 1000` - Reduce CPU usage
- `logging.level: warn` - Only warnings and errors
- `logging.format: json` - Structured logs for log aggregation
- `api.base_url: https://api.example.com` - HTTPS production URL
- `sync.sync_interval_ms: 300000` - 5 minutes for less frequent syncs
```

## Acceptance Criteria Checklist

- [ ] `sync-service/config.yaml` structure defined
- [ ] `sync-service/config.example.yaml` created with all sections
- [ ] All configuration options have inline comments
- [ ] `.gitignore` updated to exclude `config.yaml`
- [ ] `sync-service/README.md` documents all configuration options
- [ ] Development defaults vs production recommendations documented
- [ ] Validation rules documented (required fields, value ranges)
- [ ] Dependencies added: `serde_yaml`, `shellexpand`
- [ ] `src/config.rs` module created with load() method
- [ ] Unit tests pass for config deserialization
- [ ] Integration test loads config.example.yaml successfully
- [ ] All clippy warnings resolved
- [ ] Code formatted with cargo fmt
- [ ] Coverage >= 80%

## Dependencies

- **Blocks**: #15 (Configuration loaders need config files)
- **Blocks**: #17 (Sync service skeleton needs configuration)
- **Replaces**: Part of #14 (split into service-specific issues)
- **Related**: #12 (Vault utilities - uses vault path from config)

## Notes

- This issue focuses on creating the configuration file structure and basic loading
- Environment variable overrides will be added in Issue #15
- Configuration validation will be added in Issue #15
- Keep implementation simple and focused for this phase
