# YAML Configuration System for Both Services

**Epic**: Configuration Management
**Priority**: P1
**Story Points**: 3

## User Story

As a developer,
I need a YAML-based configuration system for both api-service and sync-service,
So that I can manage environment-specific settings, service behavior, and feature toggles without modifying code.

## Acceptance Criteria

### API Service Configuration
- [ ] `api-service/config.yaml` created with complete configuration structure:
  ```yaml
  database:
    url: postgresql://noosphere_user:dev_password@localhost:5432/noosphere
    pool_size: 5
    max_overflow: 10
    pool_recycle: 3600
    echo: false

  vault:
    path: ~/noosphere-vault
    categories:
      - Inbox
      - People
      - Projects
      - Ideas
      - Admin

  scheduler:
    enabled: true
    surfacing_interval: 300  # 5 minutes
    surfacing_batch_size: 10
    cleanup_interval: 3600   # 1 hour

  ai:
    classification:
      model: gemini-1.5-flash
      temperature: 0.3
      max_tokens: 1000
    embeddings:
      model: text-embedding-3-small
      dimensions: 1536
    surfacing:
      model: gemini-1.5-flash
      temperature: 0.5

  logging:
    level: INFO
    format: "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
    file: logs/api-service.log
    max_bytes: 10485760  # 10 MB
    backup_count: 5

  api:
    host: 127.0.0.1
    port: 8000
    reload: true  # Development only
    workers: 1    # Development (use 4+ in production)
  ```

### Sync Service Configuration
- [ ] `sync-service/config.yaml` created with sync service settings:
  ```yaml
  vault:
    path: ~/noosphere-vault
    watch_recursive: true
    debounce_ms: 500  # Wait 500ms after last change before syncing

  api:
    base_url: http://127.0.0.1:8000
    timeout_ms: 5000
    retry_attempts: 3
    retry_delay_ms: 1000

  sync:
    batch_size: 10
    sync_interval_ms: 60000  # Sync every 60 seconds
    ignore_patterns:
      - "*.lock"
      - "*.tmp"
      - ".DS_Store"
      - ".noosphere-metadata"

  logging:
    level: info
    format: text  # or "json"
    file: logs/sync-service.log
    max_size_mb: 10
    max_backups: 5
  ```

### Configuration Templates
- [ ] `api-service/config.example.yaml` created as template for new developers
- [ ] `sync-service/config.example.yaml` created as template for new developers
- [ ] Templates include comments explaining each configuration option
- [ ] `.gitignore` updated to exclude `config.yaml` (user-specific):
  ```gitignore
  # User-specific configuration
  config.yaml

  # Keep example templates
  !config.example.yaml
  ```

### Configuration Documentation
- [ ] `docs/configuration.md` created documenting:
  - Configuration file structure
  - All configuration options and their defaults
  - Environment-specific settings (development vs production)
  - Security considerations (sensitive values, environment variables)
  - How to override settings with environment variables (covered in EPIC-4-2)
- [ ] Configuration validation rules documented:
  - Required fields
  - Valid value ranges
  - Dependencies between settings

### Default Values
- [ ] Sensible defaults defined for all optional configuration values
- [ ] Development-oriented defaults (verbose logging, auto-reload, localhost)
- [ ] Production recommendations documented (workers, pool size, logging level)

## Technical Notes

**YAML Format Selection**:
- Human-readable and editable
- Supports comments for documentation
- Native support in Python (PyYAML) and Rust (serde_yaml)
- Industry standard for configuration files

**Configuration Sections**:
- **Database**: Connection settings, pooling configuration
- **Vault**: File system paths, category structure
- **Scheduler**: Background task intervals and batch sizes
- **AI**: Model selection, temperature, token limits
- **Logging**: Log levels, formats, rotation settings
- **API**: Server host, port, worker configuration
- **Sync**: File watching, sync intervals, ignore patterns

**Security Considerations**:
- Sensitive values (passwords, API keys) should use environment variables
- config.yaml excluded from git to prevent credential leaks
- config.example.yaml provides template with placeholder values
- Never commit real credentials to repository

**Development vs Production**:
```yaml
# Development
api:
  host: 127.0.0.1  # Localhost only
  reload: true      # Auto-reload on code changes
  workers: 1        # Single worker for debugging

# Production
api:
  host: 0.0.0.0     # Accept external connections
  reload: false     # No auto-reload
  workers: 4        # Multiple workers for performance
```

**Configuration Validation Strategy**:
- Validate on service startup (fail fast)
- Type checking (int, string, bool)
- Range checking (positive integers, valid ports)
- Path validation (directories exist, permissions)
- Model name validation (supported AI models)

**Alternative Approaches Considered**:
1. **Environment variables only**: Too many variables, hard to manage
2. **JSON configuration**: No comments, less human-readable
3. **TOML configuration**: Less common, harder for non-developers
4. **Hard-coded defaults**: Inflexible, requires code changes
5. **YAML (chosen)**: Best balance of readability, comments, tooling support

## Dependencies

- **Blocks**:
  - EPIC-4-2 (Configuration loaders need config files to load)
  - EPIC-5-1 (API service needs configuration)
  - EPIC-5-2 (Sync service needs configuration)
- **Blocked By**:
  - EPIC-1-1 (Repository structure needed for config files)
- **Related**:
  - EPIC-2-1 (Database URL configuration)
  - EPIC-3-1 (Vault path configuration)

## Verification

### Configuration File Validation
```bash
# Check api-service config exists
ls -la api-service/config.example.yaml
# Should show template file

# Check sync-service config exists
ls -la sync-service/config.example.yaml
# Should show template file

# Validate YAML syntax (Python)
cd api-service
python -c "
import yaml
with open('config.example.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('✓ Valid YAML')
    print(f'Database URL: {config[\"database\"][\"url\"]}')
    print(f'Vault path: {config[\"vault\"][\"path\"]}')
    print(f'AI model: {config[\"ai\"][\"classification\"][\"model\"]}')
"

# Validate YAML syntax (Rust)
cd sync-service
cargo add serde_yaml
cargo run --example validate_config
# Example should load config.example.yaml and print parsed values
```

### Documentation Verification
```bash
# Check documentation exists
cat docs/configuration.md

# Should explain:
# - All configuration sections
# - Default values
# - Environment variable overrides
# - Production recommendations
# - Security best practices
```

### Template Completeness Test
```bash
# Copy example to actual config
cp api-service/config.example.yaml api-service/config.yaml
cp sync-service/config.example.yaml sync-service/config.yaml

# Verify services can start with example config
cd api-service
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Check all required sections exist
assert 'database' in config
assert 'vault' in config
assert 'scheduler' in config
assert 'ai' in config
assert 'logging' in config
assert 'api' in config

print('✓ All required sections present in api-service config')
"

cd sync-service
# Similar validation for Rust config
```

### Git Ignore Verification
```bash
# Check config.yaml is ignored
git status
# Should NOT show config.yaml in untracked files

# Check example is tracked
git add config.example.yaml
git status
# Should show config.example.yaml as staged

# Verify gitignore rule
cat .gitignore | grep config.yaml
# Should show: config.yaml
```

**Completion Criteria**:
- [ ] config.example.yaml exists for both services with all sections
- [ ] Configuration structure documented in docs/configuration.md
- [ ] All configuration options have comments explaining purpose
- [ ] Sensible defaults defined for development environment
- [ ] Production recommendations documented
- [ ] config.yaml excluded from git via .gitignore
- [ ] YAML syntax valid (no parsing errors)
- [ ] Configuration validation rules documented
- [ ] Security considerations documented (no credentials in config files)
