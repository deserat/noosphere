"""Unit tests for configuration loader.

Tests configuration loading from YAML, environment variable overrides,
validation, and singleton pattern.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.config import Config, get_config, load_config


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary configuration file for testing."""
    config_file = tmp_path / "test_config.yaml"
    config_content = """
database:
  url: postgresql://test_user:test_pass@localhost/test_db
  pool_size: 3
  max_overflow: 5
  pool_pre_ping: true
  echo: false

vault:
  path: ~/test-vault

scheduler:
  enabled: true
  surfacing_interval_seconds: 3600
  batch_size: 25

ai:
  classification:
    model: gemini-1.5-flash
    temperature: 0.2
    max_tokens: 128
  embedding:
    model: text-embedding-004
    dimension: 768
  api_keys:
    gemini: test-gemini-key
    openai: test-openai-key

logging:
  level: INFO
  format: text
  file: logs/test.log

api:
  host: 127.0.0.1
  port: 9000
  debug: false
  cors_origins:
    - http://localhost:3000
  api_prefix: /api
  api_version: v1
"""
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def minimal_config_file(tmp_path):
    """Create a minimal configuration file for testing."""
    config_file = tmp_path / "minimal_config.yaml"
    config_content = """
database:
  url: postgresql://localhost/test
"""
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def reset_singleton():
    """Reset global config singleton before and after each test."""
    import app.core.config as config_module
    config_module._config_instance = None
    yield
    config_module._config_instance = None


@pytest.fixture
def clean_env():
    """Clean environment variables that might interfere with tests."""
    env_vars_to_clean = [
        "DATABASE_URL",
        "DB_POOL_SIZE",
        "DB_MAX_OVERFLOW",
        "VAULT_PATH",
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AI_MODEL",
        "LOG_LEVEL",
        "LOG_FORMAT",
        "API_HOST",
        "API_PORT",
        "API_DEBUG",
        "SURFACING_INTERVAL_SECONDS",
        "SCHEDULER_BATCH_SIZE",
    ]
    original_env = {}
    for var in env_vars_to_clean:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    yield
    # Restore original environment
    for var, value in original_env.items():
        os.environ[var] = value


def test_load_config_from_yaml(temp_config_file, reset_singleton, clean_env):
    """Test loading configuration from YAML file."""
    # Mock load_dotenv to prevent loading real .env file
    with patch("app.core.config.load_dotenv"):
        config = Config(str(temp_config_file))

    # Verify database configuration
    assert config.database["url"] == "postgresql://test_user:test_pass@localhost/test_db"
    assert config.database["pool_size"] == 3
    assert config.database["max_overflow"] == 5
    assert config.database["pool_pre_ping"] is True
    assert config.database["echo"] is False

    # Verify vault configuration (path will be expanded from ~/test-vault)
    assert config.vault["path"].endswith("test-vault") or "test-vault" in config.vault["path"]

    # Verify AI configuration
    assert config.ai["classification"]["model"] == "gemini-1.5-flash"
    assert config.ai["classification"]["temperature"] == 0.2
    assert config.ai["api_keys"]["gemini"] == "test-gemini-key"

    # Verify logging configuration
    assert config.logging["level"] == "INFO"
    assert config.logging["format"] == "text"

    # Verify API configuration
    assert config.api["host"] == "127.0.0.1"
    assert config.api["port"] == 9000
    assert config.api["debug"] is False


def test_env_override_database_url(temp_config_file, reset_singleton):
    """Test environment variable overrides YAML database URL."""
    override_url = "postgresql://override_user:override_pass@localhost/override_db"

    with patch.dict(os.environ, {"DATABASE_URL": override_url}):
        config = Config(str(temp_config_file))

        assert config.database["url"] == override_url
        # Other database settings should remain from YAML
        assert config.database["pool_size"] == 3


def test_env_override_pool_size(temp_config_file, reset_singleton):
    """Test environment variable overrides database pool size."""
    with patch.dict(os.environ, {"DB_POOL_SIZE": "10", "DB_MAX_OVERFLOW": "20"}):
        config = Config(str(temp_config_file))

        assert config.database["pool_size"] == 10
        assert config.database["max_overflow"] == 20


def test_env_override_vault_path(temp_config_file, reset_singleton, tmp_path):
    """Test environment variable overrides vault path."""
    override_path = str(tmp_path / "override-vault")
    os.makedirs(override_path, exist_ok=True)

    with patch.dict(os.environ, {"VAULT_PATH": override_path}):
        config = Config(str(temp_config_file))

        assert config.vault["path"] == override_path


def test_env_override_ai_keys(temp_config_file, reset_singleton):
    """Test environment variable overrides AI API keys."""
    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "env-gemini-key",
            "OPENAI_API_KEY": "env-openai-key",
            "ANTHROPIC_API_KEY": "env-anthropic-key",
        },
    ):
        config = Config(str(temp_config_file))

        assert config.ai["api_keys"]["gemini"] == "env-gemini-key"
        assert config.ai["api_keys"]["openai"] == "env-openai-key"
        assert config.ai["api_keys"]["anthropic"] == "env-anthropic-key"


def test_env_override_log_level(temp_config_file, reset_singleton):
    """Test environment variable overrides log level."""
    with patch.dict(os.environ, {"LOG_LEVEL": "ERROR"}):
        config = Config(str(temp_config_file))

        assert config.logging["level"] == "ERROR"


def test_env_override_api_settings(temp_config_file, reset_singleton):
    """Test environment variable overrides API server settings."""
    with patch.dict(
        os.environ, {"API_HOST": "0.0.0.0", "API_PORT": "8080", "API_DEBUG": "true"}
    ):
        config = Config(str(temp_config_file))

        assert config.api["host"] == "0.0.0.0"
        assert config.api["port"] == 8080
        assert config.api["debug"] is True


def test_env_override_scheduler(temp_config_file, reset_singleton):
    """Test environment variable overrides scheduler settings."""
    with patch.dict(
        os.environ,
        {"SURFACING_INTERVAL_SECONDS": "7200", "SCHEDULER_BATCH_SIZE": "100"},
    ):
        config = Config(str(temp_config_file))

        assert config.scheduler["surfacing_interval_seconds"] == 7200
        assert config.scheduler["batch_size"] == 100


def test_get_method_dot_notation(temp_config_file, reset_singleton, clean_env):
    """Test get() method with dot notation access."""
    with patch("app.core.config.load_dotenv"):
        config = Config(str(temp_config_file))

    # Test nested access
    assert config.get("database.url") == "postgresql://test_user:test_pass@localhost/test_db"
    assert config.get("database.pool_size") == 3
    assert config.get("ai.classification.model") == "gemini-1.5-flash"
    assert config.get("api.port") == 9000

    # Test default values
    assert config.get("nonexistent.key", "default_value") == "default_value"
    assert config.get("database.nonexistent", 42) == 42


def test_property_accessors(temp_config_file, reset_singleton, clean_env):
    """Test property accessors return correct dictionaries."""
    with patch("app.core.config.load_dotenv"):
        config = Config(str(temp_config_file))

    # Test all property accessors
    assert isinstance(config.database, dict)
    assert config.database["url"] == "postgresql://test_user:test_pass@localhost/test_db"

    assert isinstance(config.vault, dict)
    assert config.vault["path"].endswith("test-vault") or "test-vault" in config.vault["path"]

    assert isinstance(config.scheduler, dict)
    assert config.scheduler["enabled"] is True

    assert isinstance(config.ai, dict)
    assert config.ai["classification"]["model"] == "gemini-1.5-flash"

    assert isinstance(config.logging, dict)
    assert config.logging["level"] == "INFO"

    assert isinstance(config.api, dict)
    assert config.api["port"] == 9000


def test_config_singleton(temp_config_file, reset_singleton):
    """Test singleton pattern ensures single config instance."""
    config1 = load_config(str(temp_config_file))
    config2 = load_config(str(temp_config_file))

    # Both calls should return the same instance
    assert config1 is config2

    # get_config should return the same instance
    config3 = get_config()
    assert config1 is config3


def test_get_config_before_load(reset_singleton):
    """Test get_config raises error if called before load_config."""
    with pytest.raises(RuntimeError, match="Configuration not loaded"):
        get_config()


def test_config_validation_missing_database(tmp_path, reset_singleton, clean_env):
    """Test validation catches missing database configuration."""
    config_file = tmp_path / "no_database.yaml"
    config_file.write_text("vault:\n  path: ~/test")

    with patch("app.core.config.load_dotenv"):
        with pytest.raises(ValueError, match="Database configuration is required"):
            Config(str(config_file))


def test_config_validation_missing_database_url(tmp_path, reset_singleton, clean_env):
    """Test validation catches missing database URL."""
    config_file = tmp_path / "no_db_url.yaml"
    config_file.write_text("database:\n  pool_size: 5")

    with patch("app.core.config.load_dotenv"):
        with pytest.raises(ValueError, match="Database URL is required"):
            Config(str(config_file))


def test_config_validation_invalid_log_level(tmp_path, reset_singleton):
    """Test validation catches invalid log level."""
    config_file = tmp_path / "invalid_log_level.yaml"
    config_content = """
database:
  url: postgresql://localhost/test
logging:
  level: INVALID_LEVEL
"""
    config_file.write_text(config_content)

    with pytest.raises(ValueError, match="Invalid log level"):
        Config(str(config_file))


def test_config_validation_invalid_port(tmp_path, reset_singleton, clean_env):
    """Test validation catches invalid API port."""
    config_file = tmp_path / "invalid_port.yaml"
    config_content = """
database:
  url: postgresql://localhost/test
api:
  port: 99999
"""
    config_file.write_text(config_content)

    with patch("app.core.config.load_dotenv"):
        with pytest.raises(ValueError, match="Invalid API port"):
            Config(str(config_file))


def test_config_validation_invalid_pool_size(tmp_path, reset_singleton):
    """Test validation catches invalid pool size."""
    config_file = tmp_path / "invalid_pool.yaml"
    config_content = """
database:
  url: postgresql://localhost/test
  pool_size: -5
"""
    config_file.write_text(config_content)

    with pytest.raises(ValueError, match="Invalid database pool_size"):
        Config(str(config_file))


def test_config_validation_invalid_max_overflow(tmp_path, reset_singleton):
    """Test validation catches invalid max_overflow."""
    config_file = tmp_path / "invalid_overflow.yaml"
    config_content = """
database:
  url: postgresql://localhost/test
  max_overflow: -1
"""
    config_file.write_text(config_content)

    with pytest.raises(ValueError, match="Invalid database max_overflow"):
        Config(str(config_file))


def test_config_validation_vault_path_created(tmp_path, reset_singleton, clean_env, caplog):
    """Test vault path is created if missing with warning."""
    vault_path = tmp_path / "new-vault"
    config_file = tmp_path / "vault_config.yaml"
    config_content = f"""
database:
  url: postgresql://localhost/test
vault:
  path: {vault_path}
"""
    config_file.write_text(config_content)

    # Ensure vault doesn't exist before test
    assert not vault_path.exists()

    with patch("app.core.config.load_dotenv"):
        config = Config(str(config_file))

        # Vault path should be created
        assert vault_path.exists()
        assert str(vault_path) in config.vault["path"]

    # Warning should be logged
    assert "Vault path does not exist, creating" in caplog.text


def test_file_not_found_error(reset_singleton):
    """Test FileNotFoundError with helpful message."""
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        Config("nonexistent_config.yaml")


def test_empty_config_file(tmp_path, reset_singleton):
    """Test ValueError for empty configuration file."""
    empty_file = tmp_path / "empty.yaml"
    empty_file.write_text("")

    with pytest.raises(ValueError, match="Configuration file is empty"):
        Config(str(empty_file))


def test_log_level_normalization(temp_config_file, reset_singleton):
    """Test log level is normalized to uppercase."""
    with patch.dict(os.environ, {"LOG_LEVEL": "debug"}):
        config = Config(str(temp_config_file))
        assert config.logging["level"] == "DEBUG"


def test_vault_path_expansion(tmp_path, reset_singleton):
    """Test vault path supports ~ and environment variable expansion."""
    vault_dir = tmp_path / "expanded-vault"
    vault_dir.mkdir()

    config_file = tmp_path / "expand_config.yaml"
    config_content = """
database:
  url: postgresql://localhost/test
vault:
  path: ~/test-vault
"""
    config_file.write_text(config_content)

    # Mock expanduser to return our temp path
    with patch("os.path.expanduser", return_value=str(vault_dir)):
        config = Config(str(config_file))
        assert config.vault["path"] == str(vault_dir)


def test_minimal_config(minimal_config_file, reset_singleton, clean_env):
    """Test minimal configuration with only required fields."""
    with patch("app.core.config.load_dotenv"):
        config = Config(str(minimal_config_file))

    # Only database URL is required
    assert config.database["url"] == "postgresql://localhost/test"

    # Other sections may not exist
    with pytest.raises(KeyError):
        config.vault

    with pytest.raises(KeyError):
        config.ai


def test_env_override_creates_missing_sections(minimal_config_file, reset_singleton):
    """Test environment variables create missing configuration sections."""
    with patch.dict(
        os.environ,
        {
            "VAULT_PATH": "/tmp/test-vault",
            "GEMINI_API_KEY": "test-key",
            "LOG_LEVEL": "DEBUG",
            "API_PORT": "8080",
        },
    ):
        # Create vault directory to avoid validation error
        os.makedirs("/tmp/test-vault", exist_ok=True)

        config = Config(str(minimal_config_file))

        # Sections should be created from environment variables
        assert config.vault["path"] == "/tmp/test-vault"
        assert config.ai["api_keys"]["gemini"] == "test-key"
        assert config.logging["level"] == "DEBUG"
        assert config.api["port"] == 8080


def test_dotenv_loading(minimal_config_file, reset_singleton, clean_env):
    """Test .env file is loaded before configuration."""
    # Mock load_dotenv to verify it's called
    with patch("app.core.config.load_dotenv") as mock_load_dotenv:
        config = Config(str(minimal_config_file))

        # Verify load_dotenv was called
        mock_load_dotenv.assert_called_once()

    # Verify config loaded successfully
    assert config.database["url"] == "postgresql://localhost/test"


def test_env_override_invalid_db_pool_size(temp_config_file, reset_singleton, clean_env):
    """Test helpful error for invalid DB_POOL_SIZE."""
    with patch.dict(os.environ, {"DB_POOL_SIZE": "not-a-number"}):
        with patch("app.core.config.load_dotenv"):
            with pytest.raises(ValueError, match="Invalid value for DB_POOL_SIZE"):
                Config(str(temp_config_file))


def test_env_override_invalid_db_max_overflow(temp_config_file, reset_singleton, clean_env):
    """Test helpful error for invalid DB_MAX_OVERFLOW."""
    with patch.dict(os.environ, {"DB_MAX_OVERFLOW": "invalid"}):
        with patch("app.core.config.load_dotenv"):
            with pytest.raises(ValueError, match="Invalid value for DB_MAX_OVERFLOW"):
                Config(str(temp_config_file))


def test_env_override_invalid_api_port(temp_config_file, reset_singleton, clean_env):
    """Test helpful error for invalid API_PORT."""
    with patch.dict(os.environ, {"API_PORT": "abc"}):
        with patch("app.core.config.load_dotenv"):
            with pytest.raises(ValueError, match="Invalid value for API_PORT"):
                Config(str(temp_config_file))


def test_env_override_invalid_surfacing_interval(
    temp_config_file, reset_singleton, clean_env
):
    """Test helpful error for invalid SURFACING_INTERVAL_SECONDS."""
    with patch.dict(os.environ, {"SURFACING_INTERVAL_SECONDS": "not-an-int"}):
        with patch("app.core.config.load_dotenv"):
            with pytest.raises(
                ValueError, match="Invalid value for SURFACING_INTERVAL_SECONDS"
            ):
                Config(str(temp_config_file))


def test_env_override_invalid_scheduler_batch_size(
    temp_config_file, reset_singleton, clean_env
):
    """Test helpful error for invalid SCHEDULER_BATCH_SIZE."""
    with patch.dict(os.environ, {"SCHEDULER_BATCH_SIZE": "xyz"}):
        with patch("app.core.config.load_dotenv"):
            with pytest.raises(ValueError, match="Invalid value for SCHEDULER_BATCH_SIZE"):
                Config(str(temp_config_file))
