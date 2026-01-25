"""Configuration loader with YAML and environment variable support.

This module provides a configuration management system that merges YAML configuration
files with environment variable overrides, following 12-factor app methodology.

Priority order (highest to lowest):
1. Environment variables (DATABASE_URL, API_PORT, etc.)
2. .env file values (loaded via python-dotenv)
3. config.yaml values
4. Hard-coded defaults in code

Example:
    >>> from app.core.config import load_config, get_config
    >>>
    >>> # Load at startup
    >>> config = load_config("config.yaml")
    >>>
    >>> # Access throughout application
    >>> db_url = get_config().database["url"]
    >>> vault_path = get_config().get("vault.path")
"""

import logging
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Module logger
logger = logging.getLogger(__name__)

# Environment variable to config path mapping
# Format: (env_var_name, config_path, type_converter, requires_expansion)
_ENV_VAR_MAPPINGS = [
    # Database
    ("DATABASE_URL", "database.url", str, False),
    ("DB_POOL_SIZE", "database.pool_size", int, False),
    ("DB_MAX_OVERFLOW", "database.max_overflow", int, False),
    # Vault (needs path expansion)
    ("VAULT_PATH", "vault.path", str, True),
    # AI API Keys
    ("GEMINI_API_KEY", "ai.api_keys.gemini", str, False),
    ("OPENAI_API_KEY", "ai.api_keys.openai", str, False),
    ("ANTHROPIC_API_KEY", "ai.api_keys.anthropic", str, False),
    ("AI_MODEL", "ai.classification.model", str, False),
    # Logging
    ("LOG_LEVEL", "logging.level", lambda v: v.upper(), False),
    ("LOG_FORMAT", "logging.format", str, False),
    # API
    ("API_HOST", "api.host", str, False),
    ("API_PORT", "api.port", int, False),
    ("API_DEBUG", "api.debug", lambda v: v.lower() in ("true", "1", "yes"), False),
    # Scheduler
    ("SURFACING_INTERVAL_SECONDS", "scheduler.surfacing_interval_seconds", int, False),
    ("SCHEDULER_BATCH_SIZE", "scheduler.batch_size", int, False),
]


class Config:
    """Configuration loader with YAML + environment variable support.

    Loads configuration from a YAML file and applies environment variable
    overrides. Provides property accessors and dot-notation access.

    Attributes:
        _config: Internal configuration dictionary loaded from YAML
    """

    def __init__(self, config_path: str = "config.yaml"):
        """Load configuration from YAML file and environment variables.

        Args:
            config_path: Path to YAML configuration file (default: config.yaml)

        Raises:
            FileNotFoundError: If configuration file does not exist
            ValueError: If configuration validation fails
        """
        # Load .env file if present (must be done before reading env vars)
        load_dotenv()

        # Load YAML configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Hint: Copy config.example.yaml to config.yaml and customize"
            )

        with open(config_file) as f:
            self._config = yaml.safe_load(f)

        if not self._config:
            raise ValueError(
                f"Configuration file is empty: {config_path}\n"
                f"Hint: Ensure config.yaml contains valid YAML configuration"
            )

        # Override with environment variables
        self._apply_env_overrides()

        # Validate configuration
        self._validate()

    def _parse_int(self, env_var: str, value: str) -> int:
        """Parse integer from environment variable with helpful error message.

        Args:
            env_var: Name of the environment variable
            value: String value to parse

        Returns:
            Parsed integer value

        Raises:
            ValueError: If value cannot be converted to integer
        """
        try:
            return int(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid value for {env_var}: '{value}'. Must be an integer."
            ) from e

    def _set_nested(self, path: str, value: Any) -> None:
        """Set nested configuration value using dot notation path.

        Args:
            path: Dot-separated path (e.g., "database.pool_size")
            value: Value to set

        Example:
            >>> self._set_nested("database.pool_size", 10)
            >>> self._set_nested("ai.api_keys.gemini", "key123")
        """
        keys = path.split(".")
        current = self._config

        # Navigate/create nested structure
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the final value
        current[keys[-1]] = value

    def _apply_env_overrides(self) -> None:
        """Override config values from environment variables using declarative mapping.

        Environment variables take precedence over YAML configuration.
        This allows environment-specific configuration without modifying files.
        """
        for env_var, config_path, converter, needs_expansion in _ENV_VAR_MAPPINGS:
            if value_str := os.getenv(env_var):
                # Handle type conversion with proper error handling
                if converter == int:
                    value = self._parse_int(env_var, value_str)
                elif callable(converter):
                    value = converter(value_str)
                else:
                    value = value_str

                # Apply path expansion if needed (only for string values)
                if needs_expansion:
                    if isinstance(value, str):
                        value = os.path.expanduser(os.path.expandvars(value))

                # Set value using dot notation path
                self._set_nested(config_path, value)

    def _ensure_section(self, *sections: str) -> None:
        """Ensure nested configuration sections exist.

        Creates nested dictionary structure if sections don't exist.

        Args:
            *sections: Variable length list of section names (nested from outer to inner)
        """
        current = self._config
        for section in sections:
            if section not in current:
                current[section] = {}
            current = current[section]

    def _validate(self) -> None:
        """Validate configuration values.

        Performs validation checks on configuration to ensure all required
        values are present and valid.

        Raises:
            ValueError: If validation fails with helpful error message
        """
        # Validate database section exists and has required fields
        if "database" not in self._config:
            raise ValueError(
                "Database configuration is required\n"
                "Hint: Add 'database' section to config.yaml or set "
                "DATABASE_URL environment variable"
            )

        if "url" not in self._config["database"]:
            raise ValueError(
                "Database URL is required\n"
                "Hint: Set DATABASE_URL environment variable or add database.url to config.yaml"
            )

        # Validate vault path exists (create if missing with warning)
        if "vault" in self._config and "path" in self._config["vault"]:
            vault_path = Path(self._config["vault"]["path"])
            # Expand ~ and environment variables
            vault_path = Path(os.path.expanduser(os.path.expandvars(str(vault_path))))

            if not vault_path.exists():
                # Create vault directory with warning
                logger.warning(f"Vault path does not exist, creating: {vault_path}")
                vault_path.mkdir(parents=True, exist_ok=True)

            # Update config with expanded path
            self._config["vault"]["path"] = str(vault_path)

        # Validate logging level if present
        if "logging" in self._config and "level" in self._config["logging"]:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            log_level = self._config["logging"]["level"].upper()
            if log_level not in valid_levels:
                raise ValueError(
                    f"Invalid log level: {log_level}\n"
                    f"Hint: Valid levels are: {', '.join(valid_levels)}"
                )
            # Normalize to uppercase
            self._config["logging"]["level"] = log_level

        # Validate API port if present
        if "api" in self._config and "port" in self._config["api"]:
            port = self._config["api"]["port"]
            if not isinstance(port, int) or port < 1 or port > 65535:
                raise ValueError(
                    f"Invalid API port: {port}\n"
                    "Hint: Port must be an integer between 1 and 65535"
                )

        # Validate pool sizes if present
        if "database" in self._config:
            if "pool_size" in self._config["database"]:
                pool_size = self._config["database"]["pool_size"]
                if not isinstance(pool_size, int) or pool_size < 1:
                    raise ValueError(
                        f"Invalid database pool_size: {pool_size}\n"
                        "Hint: pool_size must be a positive integer"
                    )

            if "max_overflow" in self._config["database"]:
                max_overflow = self._config["database"]["max_overflow"]
                if not isinstance(max_overflow, int) or max_overflow < 0:
                    raise ValueError(
                        f"Invalid database max_overflow: {max_overflow}\n"
                        "Hint: max_overflow must be a non-negative integer"
                    )

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key_path: Dot-separated path to configuration value (e.g., "database.url")
            default: Default value if key path not found (default: None)

        Returns:
            Configuration value or default if not found

        Example:
            >>> config.get("database.pool_size")
            5
            >>> config.get("ai.classification.model", "gemini-1.5-flash")
            "gemini-1.5-flash"
        """
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
    def database(self) -> dict[str, Any]:
        """Get database configuration section.

        Returns:
            Dictionary containing database configuration (url, pool_size, etc.)

        Raises:
            KeyError: If database section is not present
        """
        return self._config["database"]

    @property
    def vault(self) -> dict[str, Any]:
        """Get vault configuration section.

        Returns:
            Dictionary containing vault configuration (path, etc.)

        Raises:
            KeyError: If vault section is not present
        """
        return self._config["vault"]

    @property
    def scheduler(self) -> dict[str, Any]:
        """Get scheduler configuration section.

        Returns:
            Dictionary containing scheduler configuration

        Raises:
            KeyError: If scheduler section is not present
        """
        return self._config["scheduler"]

    @property
    def ai(self) -> dict[str, Any]:
        """Get AI configuration section.

        Returns:
            Dictionary containing AI configuration (model, api_keys, etc.)

        Raises:
            KeyError: If ai section is not present
        """
        return self._config["ai"]

    @property
    def logging(self) -> dict[str, Any]:
        """Get logging configuration section.

        Returns:
            Dictionary containing logging configuration (level, format, etc.)

        Raises:
            KeyError: If logging section is not present
        """
        return self._config["logging"]

    @property
    def api(self) -> dict[str, Any]:
        """Get API server configuration section.

        Returns:
            Dictionary containing API configuration (host, port, etc.)

        Raises:
            KeyError: If api section is not present
        """
        return self._config["api"]


# Global config instance (singleton pattern)
_config_instance: Config | None = None


def load_config(config_path: str = "config.yaml") -> Config:
    """Load configuration (singleton pattern).

    Loads configuration from YAML file and caches it globally.
    Subsequent calls return the cached instance.

    Args:
        config_path: Path to YAML configuration file (default: config.yaml)

    Returns:
        Configuration instance

    Example:
        >>> # Load at application startup
        >>> config = load_config("config.yaml")
        >>> print(config.database["url"])
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance


def get_config() -> Config:
    """Get loaded configuration instance.

    Returns the singleton configuration instance. Must call load_config()
    before calling this function.

    Returns:
        Configuration instance

    Raises:
        RuntimeError: If configuration has not been loaded yet

    Example:
        >>> # After loading config at startup
        >>> db_url = get_config().database["url"]
        >>> vault_path = get_config().get("vault.path")
    """
    if _config_instance is None:
        raise RuntimeError(
            "Configuration not loaded. Call load_config() first.\n"
            "Hint: Add load_config() to your application startup code"
        )
    return _config_instance
