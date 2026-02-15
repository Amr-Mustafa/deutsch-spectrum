"""Configuration module for DeutschSpectrum backend."""
from pathlib import Path
import yaml
import os
from typing import Dict, Any, List, Optional

# Get config directory
CONFIG_DIR = Path(__file__).parent


def load_config(config_file: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_file: Name of the config file (default: config.yaml)

    Returns:
        Configuration dictionary
    """
    config_path = CONFIG_DIR / config_file

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_environment_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific environment.

    Args:
        environment: Environment name (development, production).
                    If None, uses default from config file or ENVIRONMENT env var.

    Returns:
        Environment configuration dictionary
    """
    config = load_config()

    # Determine environment
    if environment is None:
        environment = os.getenv('ENVIRONMENT', config.get('default_environment', 'production'))

    # Get environment-specific config
    env_config = config['environments'].get(environment, {})

    # Merge with global config
    global_config = config.get('global', {})

    # Override port with environment variable if set
    if env_config.get('port') is None:
        env_config['port'] = int(os.getenv('PORT', '8000'))

    return {
        'environment': environment,
        **global_config,
        **env_config
    }


class Config:
    """Configuration class for easy access to settings."""

    def __init__(self, environment: Optional[str] = None):
        """Initialize configuration."""
        self.config = get_environment_config(environment)

    def __getattr__(self, name: str) -> Any:
        """Get configuration value by attribute name."""
        return self.config.get(name)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default fallback."""
        return self.config.get(key, default)


# Create global config instance
config = Config()
