// Integration tests for configuration loading

use noosphere_sync::config::{Config, LogFormat, LogLevel};

#[test]
fn test_load_example_config() {
    let config = Config::load("config.example.yaml").expect("Failed to load config.example.yaml");

    // Verify vault config
    assert!(
        !config.vault.path.as_os_str().is_empty(),
        "Vault path should not be empty"
    );
    assert!(
        config.vault.watch_recursive,
        "watch_recursive should be true"
    );
    assert_eq!(config.vault.debounce_ms, 500, "debounce_ms should be 500");

    // Verify API config
    assert_eq!(
        config.api.base_url, "http://127.0.0.1:8000",
        "base_url should be localhost"
    );
    assert_eq!(config.api.timeout_ms, 5000, "timeout_ms should be 5000");
    assert_eq!(config.api.retry_attempts, 3, "retry_attempts should be 3");
    assert_eq!(
        config.api.retry_delay_ms, 1000,
        "retry_delay_ms should be 1000"
    );

    // Verify sync config
    assert_eq!(config.sync.batch_size, 10, "batch_size should be 10");
    assert_eq!(
        config.sync.sync_interval_ms, 60000,
        "sync_interval_ms should be 60000"
    );
    assert!(
        !config.sync.ignore_patterns.is_empty(),
        "ignore_patterns should not be empty"
    );
    assert_eq!(
        config.sync.ignore_patterns.len(),
        4,
        "Should have 4 default ignore patterns"
    );
    assert!(
        config.sync.ignore_patterns.contains(&"*.lock".to_string()),
        "Should ignore *.lock files"
    );
    assert!(
        config.sync.ignore_patterns.contains(&"*.tmp".to_string()),
        "Should ignore *.tmp files"
    );

    // Verify logging config
    assert_eq!(
        config.logging.level,
        LogLevel::Info,
        "log level should be info"
    );
    assert_eq!(
        config.logging.format,
        LogFormat::Text,
        "log format should be text"
    );
    assert_eq!(config.logging.max_size_mb, 10, "max_size_mb should be 10");
    assert_eq!(config.logging.max_backups, 5, "max_backups should be 5");
}

#[test]
fn test_vault_path_expansion() {
    let config = Config::load("config.example.yaml").expect("Failed to load config.example.yaml");

    let expanded_path = config.vault_path();

    // Should not contain ~ after expansion
    let path_str = expanded_path.to_string_lossy();
    assert!(
        !path_str.contains('~'),
        "Expanded path should not contain ~"
    );

    // Should contain noosphere-vault
    assert!(
        path_str.contains("noosphere-vault"),
        "Expanded path should contain noosphere-vault"
    );
}

#[test]
fn test_invalid_config_path() {
    let result = Config::load("nonexistent-config.yaml");
    assert!(result.is_err(), "Loading nonexistent config should fail");

    let error = result.unwrap_err();
    let error_msg = error.to_string();
    assert!(
        error_msg.contains("Failed to read config file"),
        "Error should mention failed to read"
    );
}
