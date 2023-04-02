import json
import os
import sys
from typing import Any, Optional

cache_dir = os.path.dirname(os.path.abspath(__file__)) + "/.cache"


def get_config(name: str, default: Optional[dict] = None) -> dict[str, Any]:
    """Gets the config."""
    assert name.endswith(".json")
    default = default or {}
    try:
        config_file = os.path.join(cache_dir, name)
        if os.path.exists(config_file):
            with open(config_file, "r") as fd:
                config = json.load(fd)
        else:
            config = default
        return config
    except Exception as ex:
        sys.stderr.write(f"Error loading config: {ex}\n")
        return default


def save_config(name: str, config: dict[str, Any]) -> None:
    """Saves the config."""
    assert name.endswith(".json")
    try:
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        config_file = os.path.join(cache_dir, name)
        with open(config_file, "w") as fd:
            json.dump(config, fd, indent=4)
    except Exception as ex:
        sys.stderr.write(f"Error saving config: {ex}\n")
