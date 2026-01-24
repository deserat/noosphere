// Configuration module for sync-service
//
// Defines YAML-based configuration structure for vault watching, API client,
// sync behavior, and logging settings.

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

/// Main configuration container
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Config {
    pub vault: VaultConfig,
    pub api: ApiConfig,
    pub sync: SyncConfig,
    pub logging: LoggingConfig,
}

/// Vault file system configuration
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct VaultConfig {
    /// Path to vault directory (supports ~ expansion)
    pub path: PathBuf,
    /// Watch subdirectories recursively
    pub watch_recursive: bool,
    /// Debounce delay in milliseconds (wait after last change before syncing)
    pub debounce_ms: u64,
}

/// API client configuration
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ApiConfig {
    /// Base URL of api-service (e.g., http://127.0.0.1:8000)
    pub base_url: String,
    /// Request timeout in milliseconds
    pub timeout_ms: u64,
    /// Number of retry attempts on failure
    pub retry_attempts: u32,
    /// Delay between retries in milliseconds
    pub retry_delay_ms: u64,
}

/// Sync behavior configuration
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct SyncConfig {
    /// Number of files to process per batch
    pub batch_size: usize,
    /// Periodic sync interval in milliseconds
    pub sync_interval_ms: u64,
    /// File patterns to ignore (glob patterns)
    pub ignore_patterns: Vec<String>,
}

/// Log level enumeration
#[derive(Debug, Clone, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum LogLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
}

/// Log format enumeration
#[derive(Debug, Clone, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum LogFormat {
    Text,
    Json,
}

/// Logging configuration
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct LoggingConfig {
    /// Log level: trace, debug, info, warn, error
    pub level: LogLevel,
    /// Log format: text (human-readable) or json (structured)
    pub format: LogFormat,
    /// Log file path
    pub file: PathBuf,
    /// Maximum log file size in megabytes before rotation
    pub max_size_mb: u64,
    /// Number of rotated log files to keep
    pub max_backups: u32,
}

impl Config {
    /// Load configuration from YAML file
    ///
    /// # Arguments
    ///
    /// * `path` - Path to YAML configuration file
    ///
    /// # Returns
    ///
    /// Parsed configuration or error if file cannot be read or parsed
    ///
    /// # Example
    ///
    /// ```no_run
    /// use noosphere_sync::config::Config;
    ///
    /// let config = Config::load("config.yaml")?;
    /// println!("Vault path: {:?}", config.vault.path);
    /// # Ok::<(), anyhow::Error>(())
    /// ```
    pub fn load(path: &str) -> Result<Self> {
        let config_str = fs::read_to_string(path)
            .with_context(|| format!("Failed to read config file: {}", path))?;

        let config: Config = serde_yaml::from_str(&config_str)
            .with_context(|| "Failed to parse YAML configuration")?;

        Ok(config)
    }

    /// Get vault path with shell expansion applied
    ///
    /// Expands ~ to user's home directory
    ///
    /// # Example
    ///
    /// ```no_run
    /// use noosphere_sync::config::Config;
    ///
    /// let config = Config::load("config.yaml")?;
    /// let expanded_path = config.vault_path();
    /// // ~/noosphere-vault becomes /home/user/noosphere-vault
    /// # Ok::<(), anyhow::Error>(())
    /// ```
    pub fn vault_path(&self) -> PathBuf {
        let path_str = self.vault.path.to_string_lossy();
        let expanded = shellexpand::tilde(&path_str);
        PathBuf::from(expanded.as_ref())
    }
}

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
    - "*.tmp"

logging:
  level: info
  format: text
  file: logs/test.log
  max_size_mb: 10
  max_backups: 5
"#;

        let config: Config = serde_yaml::from_str(yaml).unwrap();

        // Verify vault config
        assert!(config.vault.watch_recursive);
        assert_eq!(config.vault.debounce_ms, 500);

        // Verify API config
        assert_eq!(config.api.base_url, "http://localhost:8000");
        assert_eq!(config.api.timeout_ms, 5000);
        assert_eq!(config.api.retry_attempts, 3);
        assert_eq!(config.api.retry_delay_ms, 1000);

        // Verify sync config
        assert_eq!(config.sync.batch_size, 10);
        assert_eq!(config.sync.sync_interval_ms, 60000);
        assert_eq!(config.sync.ignore_patterns.len(), 2);
        assert_eq!(config.sync.ignore_patterns[0], "*.lock");

        // Verify logging config
        assert_eq!(config.logging.level, LogLevel::Info);
        assert_eq!(config.logging.format, LogFormat::Text);
        assert_eq!(config.logging.max_size_mb, 10);
        assert_eq!(config.logging.max_backups, 5);
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
        assert!(config.logging.file.to_string_lossy().contains("test.log"));
    }

    #[test]
    fn test_vault_path_expansion() {
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
        let expanded = config.vault_path();

        // Should not contain ~ after expansion
        assert!(!expanded.to_string_lossy().contains('~'));
        // Should contain test-vault
        assert!(expanded.to_string_lossy().contains("test-vault"));
    }

    #[test]
    fn test_missing_required_field() {
        // Missing vault section
        let yaml = r#"
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

        let result: Result<Config, _> = serde_yaml::from_str(yaml);
        assert!(result.is_err());
    }

    #[test]
    fn test_invalid_log_level() {
        // Invalid log level should fail deserialization
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
  level: invalid
  format: text
  file: logs/test.log
  max_size_mb: 10
  max_backups: 5
"#;

        let result: Result<Config, _> = serde_yaml::from_str(yaml);
        assert!(result.is_err());
    }

    #[test]
    fn test_invalid_log_format() {
        // Invalid log format should fail deserialization
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
  format: invalid
  file: logs/test.log
  max_size_mb: 10
  max_backups: 5
"#;

        let result: Result<Config, _> = serde_yaml::from_str(yaml);
        assert!(result.is_err());
    }
}
