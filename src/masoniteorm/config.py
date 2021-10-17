import os
import pydoc

from .exceptions import ConfigurationNotFound


def load_config(config_path=None):
    """Load ORM configuration from given configuration path (dotted or not).
    If no path is provided:
        1. try to load from DB_CONFIG_PATH environment variable
        2. else try to load from default config_path: config/database
    """
    selected_config_path = (
        config_path or os.getenv("DB_CONFIG_PATH", None) or "config/database"
    )
    # format path as python module if needed
    selected_config_path = selected_config_path.replace("/", ".").rstrip(".py")
    config_module = pydoc.locate(selected_config_path)
    if config_module is None:
        raise ConfigurationNotFound(
            f"ORM configuration file has not been found in {selected_config_path}."
        )
    return config_module
