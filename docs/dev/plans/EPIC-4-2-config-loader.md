# Plan: Implement Configuration Loader for API Service (Issue #15)

## Issue Summary

**Issue #15**: Configuration Loaders with Environment Variable Support
**Epic**: EPIC-4 (Configuration System)
**Priority**: P1
**Story Points**: 5 (Medium)
**Service**: api-service (Python/FastAPI)

**Goal**: Create a configuration loader that merges YAML files with environment variables, enabling environment-specific overrides without modifying config files.

## Current State

### Existing Infrastructure ✅
- `api-service/app/core/` directory exists (empty - ready for config.py)
- Dependencies installed: `python-dotenv>=1.0.0`, `pyyaml>=6.0.1`
- `.env` file exists with environment variables (DATABASE_URL, VAULT_PATH, etc.)
- Database models and session management implemented
- Current pattern: Raw `os.getenv()` calls in `app/db/session.py`

### What Needs to Be Created ❌
1. `api-service/app/core/config.py` - Configuration loader module
2. `api-service/config.yaml` - YAML configuration template
3. `api-service/config.example.yaml` - Example configuration (git-tracked)
4. `.env.example` update - Document all supported environment variables
5. Tests for configuration loading and validation

## Implementation Plan

### Phase 1: Create Configuration Loader Module

**File**: `api-service/app/core/config.py`

**Key Components**:

1. **Config Class**:
   - Load YAML configuration from `config.yaml`
   - Load `.env` file using python-dotenv
   - Apply environment variable overrides
   - Provide property accessors for config sections
   - Support dot-notation access (e.g., `get("database.url")`)
   - Singleton pattern for global access

2. **Environment Variable Overrides**:
   ```python
   Priority order (highest to lowest):
   1. Environment variables (DATABASE_URL, API_PORT, etc.)
   2. .env file values (loaded via python-dotenv)
   3. config.yaml values
   4. Hard-coded defaults in code
   ```

3. **Configuration Sections** (matching api-service needs):
   - `database`: Database connection settings (url, pool_size, echo, etc.)
   - `vault`: Vault path configuration
   - `scheduler`: Surfacing scheduler settings (interval, batch_size, etc.)
   - `ai`: AI/LLM settings (model, api_keys, temperature, etc.)
   - `logging`: Logging configuration (level, format, file, etc.)
   - `api`: API server settings (host, port, cors, etc.)

4. **Helper Functions**:
   - `load_config(config_path)` - Load and initialize configuration (singleton)
   - `get_config()` - Get loaded configuration instance
   - Raise helpful errors if config not loaded

### Phase 2: Create YAML Configuration Files

**File**: `api-service/config.example.yaml`

**Structure** (adapted from sync-service pattern):
```yaml
# Noosphere API Service Configuration

database:
  url: postgresql://noosphere_user:dev_password@localhost:5432/noosphere
  pool_size: 5
  max_overflow: 10
  pool_pre_ping: true
  echo: false

vault:
  path: ~/noosphere-vault

scheduler:
  enabled: true
  surfacing_interval_seconds: 86400  # 24 hours
  batch_size: 50

ai:
  classification:
    model: gemini-1.5-flash
    temperature: 0.1
    max_tokens: 256
  api_keys:
    gemini: ${GEMINI_API_KEY}  # Set via environment variable
    openai: ${OPENAI_API_KEY}  # Set via environment variable

logging:
  level: INFO
  format: text  # text or json
  file: logs/api-service.log

api:
  host: 127.0.0.1
  port: 8000
  debug: false
  cors_origins:
    - http://localhost:3000
    - http://localhost:8000
```

**File**: `api-service/config.yaml` (user-specific, not tracked)
- Copy of config.example.yaml
- Customized for local environment
- Added to .gitignore (already present)

### Phase 3: Update .env.example

**File**: `api-service/.env.example`

Add comprehensive documentation:
```bash
# ==============================================
# Noosphere API Service Environment Variables
# ==============================================
#
# Priority: Environment variables override config.yaml
# Setup: cp .env.example .env and customize
#

# ----------------------------------------------
# Database Configuration
# ----------------------------------------------
DATABASE_URL=postgresql://noosphere_user:dev_password@localhost:5432/noosphere
DB_POOL_SIZE=5

# ----------------------------------------------
# Vault Configuration
# ----------------------------------------------
VAULT_PATH=~/noosphere-vault

# ----------------------------------------------
# AI API Keys (REQUIRED for classification)
# ----------------------------------------------
# Get keys from:
# - Gemini: https://aistudio.google.com/app/apikey
# - OpenAI: https://platform.openai.com/api-keys
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# ----------------------------------------------
# Logging Configuration
# ----------------------------------------------
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# ----------------------------------------------
# API Server Configuration
# ----------------------------------------------
API_HOST=127.0.0.1
API_PORT=8000
API_DEBUG=false

# ----------------------------------------------
# Scheduler Configuration
# ----------------------------------------------
SURFACING_INTERVAL_SECONDS=86400
```

### Phase 4: Implement Validation

**Validation Logic in Config Class**:

1. **Required Fields Check**:
   - Database URL must be provided
   - Vault path must exist
   - At least one AI API key configured

2. **Type Validation**:
   - Port numbers must be integers
   - Pool sizes must be positive integers
   - Log level must be valid (DEBUG, INFO, WARNING, ERROR, CRITICAL)

3. **Path Validation**:
   - Vault path exists (create if missing with warning)
   - Log directory exists (create if missing)

4. **Helpful Error Messages**:
   ```python
   Error: Configuration file not found: config.yaml
   Hint: Copy config.example.yaml to config.yaml and customize

   Error: Invalid vault path: /nonexistent/path
   Hint: Create the vault directory or update vault.path in config.yaml

   Error: No AI API keys configured
   Hint: Set GEMINI_API_KEY or OPENAI_API_KEY in .env file
   ```

### Phase 5: Write Tests

**File**: `api-service/tests/unit/core/test_config.py`

**Test Cases**:
1. `test_load_config_from_yaml` - Loads YAML configuration correctly
2. `test_env_override_database_url` - Environment variable overrides YAML
3. `test_env_override_log_level` - Environment variable overrides YAML
4. `test_get_method_dot_notation` - Dot notation access works
5. `test_property_accessors` - Property accessors return correct values
6. `test_config_singleton` - Singleton pattern enforced
7. `test_config_validation_missing_database` - Validation catches missing DB URL
8. `test_config_validation_invalid_vault_path` - Validation catches bad paths
9. `test_load_dotenv` - .env file loaded before config

**Coverage Target**: 90%+ (includes all code paths)

### Phase 6: Integration with Existing Code

**Update Required Files**:

1. **`app/db/session.py`** (lines 21-23):
   - Replace raw `os.getenv("DATABASE_URL")` with `get_config().database["url"]`
   - Ensure config is loaded at application startup

2. **`app/main.py`** (when created):
   - Call `load_config()` at startup (before database init)
   - Log configuration summary (non-sensitive values)

## Files to Create/Modify

### New Files:
1. `api-service/app/core/config.py` (~150 lines) - Configuration loader
2. `api-service/config.example.yaml` (~80 lines) - Example configuration
3. `api-service/tests/unit/core/test_config.py` (~200 lines) - Tests
4. `api-service/tests/unit/core/__init__.py` - Package init

### Modified Files:
1. `api-service/.env.example` - Add comprehensive environment variable docs
2. `api-service/app/core/__init__.py` - Export config functions
3. `api-service/.gitignore` - Ensure config.yaml ignored (already present)

### User-Created Files (not tracked):
1. `api-service/config.yaml` - User's local configuration (copy from example)
2. `api-service/.env` - User's environment variables (copy from .env.example)

## Architecture Decisions

### 1. Why Singleton Pattern?
- Load configuration once at startup (not on every access)
- Avoid re-reading YAML file repeatedly
- Global access via `get_config()` function
- Thread-safe (Python GIL ensures singleton creation safety)

### 2. Why Separate config.yaml and .env?
- **config.yaml**: Non-sensitive settings, structure, defaults
- **.env**: Secrets (API keys, passwords), environment-specific values
- Follows 12-factor app methodology
- Allows version control of structure (config.example.yaml) but not secrets

### 3. Environment Variable Naming Convention
- **Format**: SCREAMING_SNAKE_CASE (e.g., DATABASE_URL, LOG_LEVEL)
- **Consistency**: Same names across Python and Rust services
- **Clarity**: Descriptive names (GEMINI_API_KEY not just API_KEY)

### 4. Configuration Validation Strategy
- **Fail Fast**: Validate at startup, not at runtime
- **Helpful Errors**: Guide users to fix problems
- **Required vs Optional**: Clear distinction in validation
- **Path Expansion**: Support ~ and environment variables in paths

## Security Best Practices

1. **Never Commit Secrets**:
   - `.env` in .gitignore
   - `config.yaml` in .gitignore (may contain sensitive paths)
   - Only `config.example.yaml` tracked

2. **Never Log Secrets**:
   - Mask API keys in logs
   - Don't log full DATABASE_URL (contains password)
   - Configuration summary excludes sensitive values

3. **Environment Variables for Secrets**:
   - API keys ONLY via environment variables
   - Database passwords via DATABASE_URL environment variable
   - Never hard-code secrets in YAML files

## Testing Strategy

### Unit Tests:
- Configuration loading from YAML
- Environment variable overrides
- Validation logic
- Error handling
- Singleton pattern

### Integration Tests:
- Full config load with .env + YAML + overrides
- Database connection using loaded config
- Vault path resolution and validation

### Manual Verification:
```bash
# Test basic loading
cd api-service
python -c "from app.core.config import load_config; cfg = load_config('config.example.yaml'); print(cfg.database)"

# Test environment override
export DATABASE_URL="postgresql://override@localhost/test"
python -c "from app.core.config import Config; cfg = Config('config.example.yaml'); assert 'override' in cfg.database['url']"

# Test validation
python -c "from app.core.config import Config; Config('nonexistent.yaml')"
# Should error with helpful message
```

## Acceptance Criteria Checklist

From Issue #15:

- [ ] `api-service/app/core/config.py` created with Config class
- [ ] Config loads YAML configuration from file
- [ ] python-dotenv loads .env file
- [ ] Environment variables override YAML values
- [ ] Config provides property accessors (database, vault, ai, etc.)
- [ ] Config provides `get()` method with dot notation
- [ ] Singleton pattern via `load_config()` and `get_config()`
- [ ] Configuration validation on load (required fields, types, paths)
- [ ] Helpful error messages for configuration problems
- [ ] `.env.example` updated with all supported environment variables
- [ ] `config.example.yaml` created as template
- [ ] Tests written with 90%+ coverage
- [ ] All tests pass

## Dependencies

**Blocked By**:
- ✅ EPIC-1-2: Python environment (python-dotenv, pyyaml installed)
- ✅ EPIC-4-1: Configuration files structure defined

**Blocks**:
- EPIC-5-1: API service startup (needs config loader)
- EPIC-5-2: Sync service integration (needs consistent config pattern)
- Database connection refactoring (replace raw os.getenv)

## Verification Commands

After implementation:

```bash
cd api-service

# Run tests
uv run pytest tests/unit/core/test_config.py -v

# Coverage check
uv run pytest tests/unit/core/test_config.py --cov=app/core/config --cov-report=term-missing

# Manual test
uv run python -c "
from app.core.config import load_config, get_config

# Load configuration
config = load_config('config.example.yaml')

# Test accessors
assert config.database['pool_size'] == 5
assert config.get('database.pool_size') == 5
assert config.vault['path'] == '~/noosphere-vault'

print('✓ Configuration loader working correctly')
"

# Test environment override
export LOG_LEVEL=ERROR
uv run python -c "
from app.core.config import Config
cfg = Config('config.example.yaml')
assert cfg.logging['level'] == 'ERROR'
print('✓ Environment override working')
"
```

## Estimated Effort

- **Config module implementation**: 2-3 hours
- **YAML configuration files**: 1 hour
- **Test suite**: 2-3 hours
- **Integration with existing code**: 1 hour
- **Documentation and verification**: 1 hour
- **Total**: ~7-10 hours (Medium story - 5 points)

## Success Criteria

Issue #15 (Python portion) complete when:

1. ✅ Configuration loader implemented with all required features
2. ✅ YAML and .env file support working
3. ✅ Environment variable overrides functional
4. ✅ Validation catches configuration problems
5. ✅ Tests pass with 90%+ coverage
6. ✅ Example files created (.env.example, config.example.yaml)
7. ✅ Helpful error messages guide users to fix issues
8. ✅ Singleton pattern ensures config loaded once

## Out of Scope (Future Enhancements)

- Configuration hot reload (SIGHUP handler)
- Configuration web UI/admin panel
- Remote configuration (Consul, etcd)
- Configuration schema validation (Pydantic model)
- Encrypted configuration values
- Configuration change auditing

These can be added in Phase 2+ once basic config system is stable.
