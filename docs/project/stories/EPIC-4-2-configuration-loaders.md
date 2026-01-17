# Configuration Loaders with Environment Variable Support

**Epic**: Configuration Management
**Priority**: P1
**Story Points**: 5

## User Story

As a developer,
I need configuration loaders that merge YAML files with environment variables,
So that I can override configuration values per environment without modifying config files.

## Acceptance Criteria

### Python Configuration Loader (API Service)
- [ ] `api-service/app/core/config.py` created with configuration loading logic:
  ```python
  import os
  import yaml
  from pathlib import Path
  from typing import Any, Dict
  from dotenv import load_dotenv

  class Config:
      """Configuration loader with YAML + environment variable support."""

      def __init__(self, config_path: str = "config.yaml"):
          """Load configuration from YAML file and environment variables."""
          load_dotenv()  # Load .env file if present

          # Load YAML configuration
          config_file = Path(config_path)
          if not config_file.exists():
              raise FileNotFoundError(f"Configuration file not found: {config_path}")

          with open(config_file, 'r') as f:
              self._config = yaml.safe_load(f)

          # Override with environment variables
          self._apply_env_overrides()

      def _apply_env_overrides(self):
          """Override config values from environment variables."""
          # Database
          if db_url := os.getenv("DATABASE_URL"):
              self._config["database"]["url"] = db_url
          if pool_size := os.getenv("DB_POOL_SIZE"):
              self._config["database"]["pool_size"] = int(pool_size)

          # Vault
          if vault_path := os.getenv("VAULT_PATH"):
              self._config["vault"]["path"] = os.path.expanduser(vault_path)

          # AI
          if api_key := os.getenv("GEMINI_API_KEY"):
              self._config.setdefault("ai", {}).setdefault("api_keys", {})["gemini"] = api_key
          if api_key := os.getenv("OPENAI_API_KEY"):
              self._config.setdefault("ai", {}).setdefault("api_keys", {})["openai"] = api_key

          # Logging
          if log_level := os.getenv("LOG_LEVEL"):
              self._config["logging"]["level"] = log_level.upper()

          # API
          if host := os.getenv("API_HOST"):
              self._config["api"]["host"] = host
          if port := os.getenv("API_PORT"):
              self._config["api"]["port"] = int(port)

      def get(self, key_path: str, default: Any = None) -> Any:
          """Get configuration value using dot notation."""
          keys = key_path.split(".")
          value = self._config

          for key in keys:
              if isinstance(value, dict):
                  value = value.get(key)
                  if value is None:
                      return default
              else:
                  return default

          return value

      @property
      def database(self) -> Dict:
          return self._config["database"]

      @property
      def vault(self) -> Dict:
          return self._config["vault"]

      @property
      def scheduler(self) -> Dict:
          return self._config["scheduler"]

      @property
      def ai(self) -> Dict:
          return self._config["ai"]

      @property
      def logging(self) -> Dict:
          return self._config["logging"]

      @property
      def api(self) -> Dict:
          return self._config["api"]

  # Global config instance
  _config_instance = None

  def load_config(config_path: str = "config.yaml") -> Config:
      """Load configuration (singleton pattern)."""
      global _config_instance
      if _config_instance is None:
          _config_instance = Config(config_path)
      return _config_instance

  def get_config() -> Config:
      """Get loaded configuration instance."""
      if _config_instance is None:
          raise RuntimeError("Configuration not loaded. Call load_config() first.")
      return _config_instance
  ```

### Rust Configuration Module (Sync Service)
- [ ] `sync-service/src/config.rs` created with Rust configuration logic:
  ```rust
  use anyhow::{Context, Result};
  use serde::{Deserialize, Serialize};
  use std::fs;
  use std::path::{Path, PathBuf};

  #[derive(Debug, Clone, Deserialize, Serialize)]
  pub struct Config {
      pub vault: VaultConfig,
      pub api: ApiConfig,
      pub sync: SyncConfig,
      pub logging: LoggingConfig,
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

  #[derive(Debug, Clone, Deserialize, Serialize)]
  pub struct LoggingConfig {
      pub level: String,
      pub format: String,
      pub file: PathBuf,
      pub max_size_mb: u64,
      pub max_backups: u32,
  }

  impl Config {
      /// Load configuration from YAML file with environment variable overrides
      pub fn load<P: AsRef<Path>>(path: P) -> Result<Self> {
          let config_path = path.as_ref();
          let config_str = fs::read_to_string(config_path)
              .with_context(|| format!("Failed to read config file: {:?}", config_path))?;

          let mut config: Config = serde_yaml::from_str(&config_str)
              .with_context(|| "Failed to parse YAML configuration")?;

          // Apply environment variable overrides
          config.apply_env_overrides();

          // Validate configuration
          config.validate()?;

          Ok(config)
      }

      /// Override config values from environment variables
      fn apply_env_overrides(&mut self) {
          // Vault path
          if let Ok(vault_path) = std::env::var("VAULT_PATH") {
              self.vault.path = shellexpand::tilde(&vault_path).into_owned().into();
          }

          // API base URL
          if let Ok(api_url) = std::env::var("API_BASE_URL") {
              self.api.base_url = api_url;
          }

          // Logging level
          if let Ok(log_level) = std::env::var("LOG_LEVEL") {
              self.logging.level = log_level.to_lowercase();
          }

          // Sync interval
          if let Ok(interval) = std::env::var("SYNC_INTERVAL_MS") {
              if let Ok(ms) = interval.parse::<u64>() {
                  self.sync.sync_interval_ms = ms;
              }
          }
      }

      /// Validate configuration values
      fn validate(&self) -> Result<()> {
          // Validate vault path exists
          if !self.vault.path.exists() {
              anyhow::bail!("Vault path does not exist: {:?}", self.vault.path);
          }

          // Validate API URL format
          if !self.api.base_url.starts_with("http://")
              && !self.api.base_url.starts_with("https://") {
              anyhow::bail!("API base URL must start with http:// or https://");
          }

          // Validate log level
          let valid_levels = ["trace", "debug", "info", "warn", "error"];
          if !valid_levels.contains(&self.logging.level.as_str()) {
              anyhow::bail!("Invalid log level: {}", self.logging.level);
          }

          Ok(())
      }

      /// Get vault path with shell expansion
      pub fn vault_path(&self) -> PathBuf {
          shellexpand::tilde(&self.vault.path.to_string_lossy())
              .into_owned()
              .into()
      }
  }

  /// Load configuration from default path
  pub fn load_default() -> Result<Config> {
      Config::load("config.yaml")
  }
  ```

### Environment Variable Precedence
- [ ] Environment variables override YAML configuration:
  ```bash
  # Priority order (highest to lowest):
  # 1. Environment variables (DATABASE_URL, API_PORT, etc.)
  # 2. .env file values (loaded via python-dotenv)
  # 3. config.yaml values
  # 4. Hard-coded defaults in code
  ```
- [ ] Documented environment variable naming convention:
  - Python: SCREAMING_SNAKE_CASE (DATABASE_URL, LOG_LEVEL)
  - Rust: SCREAMING_SNAKE_CASE (VAULT_PATH, API_BASE_URL)
  - Consistent naming across both services

### Configuration Access Helpers
- [ ] Python helper functions:
  ```python
  # Usage example
  from app.core.config import load_config, get_config

  # Load at startup
  config = load_config("config.yaml")

  # Access throughout application
  db_url = get_config().database["url"]
  vault_path = get_config().get("vault.path")
  ai_model = get_config().get("ai.classification.model", "gemini-1.5-flash")
  ```
- [ ] Rust helper methods:
  ```rust
  // Usage example
  use crate::config::Config;

  // Load at startup
  let config = Config::load("config.yaml")?;

  // Access throughout application
  let vault_path = config.vault_path();
  let api_url = &config.api.base_url;
  let log_level = &config.logging.level;
  ```

### Validation and Error Handling
- [ ] Configuration validation on load:
  - Required fields present
  - Valid value types (int, string, bool)
  - Valid value ranges (positive integers, valid ports)
  - Path existence checks (vault directory)
  - Model name validation (supported AI models)
- [ ] Helpful error messages for configuration problems:
  ```
  Error: Configuration file not found: config.yaml
  Hint: Copy config.example.yaml to config.yaml and customize

  Error: Invalid vault path: /nonexistent/path
  Hint: Create the vault directory or update vault.path in config.yaml

  Error: Invalid log level: VERBOSE
  Hint: Valid levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL
  ```

### .env File Support
- [ ] `.env.example` created with all supported environment variables:
  ```bash
  # Database
  DATABASE_URL=postgresql://noosphere_user:dev_password@localhost:5432/noosphere
  DB_POOL_SIZE=5

  # Vault
  VAULT_PATH=~/noosphere-vault

  # AI API Keys
  GEMINI_API_KEY=your-gemini-api-key-here
  OPENAI_API_KEY=your-openai-api-key-here

  # Logging
  LOG_LEVEL=INFO

  # API Server
  API_HOST=127.0.0.1
  API_PORT=8000

  # Sync Service
  SYNC_INTERVAL_MS=60000
  ```
- [ ] `.env` added to `.gitignore` (never commit secrets)
- [ ] Documentation explains when to use .env vs config.yaml:
  - .env: Secrets (API keys, passwords), environment-specific values
  - config.yaml: Non-sensitive settings, default values, structure

## Technical Notes

**Environment Variable Override Pattern**:
```python
# Python: Walrus operator for concise override
if db_url := os.getenv("DATABASE_URL"):
    config["database"]["url"] = db_url

# Rust: Pattern matching for type safety
if let Ok(vault_path) = std::env::var("VAULT_PATH") {
    self.vault.path = vault_path.into();
}
```

**Singleton Pattern for Configuration**:
- Load once at application startup
- Avoid re-reading YAML file on every access
- Global access via get_config() function

**Validation Strategy**:
- **Fail Fast**: Validate at startup, not at runtime
- **Type Safety**: Rust enforces types at compile time, Python validates at load time
- **Path Expansion**: Support ~ and environment variables in paths
- **Helpful Errors**: Guide users to fix configuration problems

**Security Best Practices**:
- Never commit .env file to git
- Never log sensitive configuration values (API keys, passwords)
- Use environment variables for secrets, not config files
- Provide .env.example with placeholder values

**Configuration Hot Reload** (Future Enhancement):
- Phase 1: Configuration loaded once at startup (simple, fast)
- Phase 2+: File watching for configuration changes (SIGHUP handler)
- Not required for MVP but design allows future extension

## Dependencies

- **Blocks**:
  - EPIC-5-1 (API service needs config loader at startup)
  - EPIC-5-2 (Sync service needs config module at startup)
- **Blocked By**:
  - EPIC-1-2 (Python environment needs PyYAML, python-dotenv)
  - EPIC-4-1 (Configuration files needed to load)
- **Related**:
  - EPIC-2-3 (Database connection uses loaded configuration)
  - EPIC-3-1 (Vault utilities use loaded vault path)

## Verification

### Python Loader Test
```bash
cd api-service
source venv/bin/activate

# Create test config
cat > test_config.yaml << EOF
database:
  url: postgresql://test_user:test_pass@localhost/test_db
  pool_size: 3
vault:
  path: ~/test-vault
ai:
  classification:
    model: gemini-1.5-flash
logging:
  level: DEBUG
api:
  port: 9000
EOF

# Test loader
python -c "
from app.core.config import Config

# Load config
config = Config('test_config.yaml')

# Test access
assert config.database['url'] == 'postgresql://test_user:test_pass@localhost/test_db'
assert config.get('database.pool_size') == 3
assert config.get('vault.path') == '~/test-vault'
assert config.get('ai.classification.model') == 'gemini-1.5-flash'

print('✓ Python config loader working')

# Test environment override
import os
os.environ['DATABASE_URL'] = 'postgresql://override_user:override_pass@localhost/override_db'
os.environ['LOG_LEVEL'] = 'ERROR'

config = Config('test_config.yaml')
assert config.database['url'] == 'postgresql://override_user:override_pass@localhost/override_db'
assert config.logging['level'] == 'ERROR'

print('✓ Environment variable overrides working')
"

rm test_config.yaml
```

### Rust Loader Test
```bash
cd sync-service

# Create test config
cat > test_config.yaml << EOF
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
EOF

# Create test vault directory
mkdir -p ~/test-vault

# Test loader
cargo test config_loader -- --nocapture

# Expected test output:
# test config_loader::load ... ok
# test config_loader::env_override ... ok
# test config_loader::validation ... ok

# Cleanup
rm test_config.yaml
rm -rf ~/test-vault
```

### Environment Variable Test
```bash
# Test .env file loading
cat > .env << EOF
DATABASE_URL=postgresql://env_user:env_pass@localhost/env_db
LOG_LEVEL=WARNING
GEMINI_API_KEY=test-gemini-key
EOF

cd api-service
python -c "
from app.core.config import Config

config = Config('config.yaml')

# Verify .env values loaded
assert 'env_user' in config.database['url']
assert config.logging['level'] == 'WARNING'

print('✓ .env file loading working')
"

rm .env
```

### Validation Test
```bash
# Test invalid configuration
cat > invalid_config.yaml << EOF
vault:
  path: /nonexistent/vault/path
logging:
  level: INVALID_LEVEL
EOF

cd sync-service
cargo run --example validate_config invalid_config.yaml

# Expected error:
# Error: Vault path does not exist: "/nonexistent/vault/path"

cd ../api-service
python -c "
from app.core.config import Config
try:
    config = Config('invalid_config.yaml')
except Exception as e:
    print(f'✓ Validation error caught: {e}')
"

rm invalid_config.yaml
```

**Completion Criteria**:
- [ ] Python config loader implemented with environment variable support
- [ ] Rust config module implemented with environment variable support
- [ ] Configuration validation on load with helpful error messages
- [ ] .env file support with .env.example template
- [ ] Environment variables override YAML configuration values
- [ ] Singleton pattern ensures config loaded once at startup
- [ ] Path expansion supports ~ and environment variables
- [ ] Configuration access helpers (get() method, property accessors)
- [ ] All configuration tests pass (load, override, validation)
- [ ] Documentation explains precedence order and best practices
