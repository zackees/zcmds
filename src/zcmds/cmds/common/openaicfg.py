import json
import os

from appdirs import user_config_dir  # type: ignore


def get_config_path() -> str:
    env_path = user_config_dir("zcmds", "zcmds", roaming=True)
    config_file = os.path.join(env_path, "openai.json")
    return config_file


def save_config(config: dict) -> None:
    config_file = get_config_path()
    # make all subdirs of config_file
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, "w") as f:
        json.dump(config, f)


def create_or_load_config() -> dict:
    config_file = get_config_path()
    try:
        with open(config_file) as f:
            config = json.loads(f.read())
        return config
    except OSError:
        save_config({})
        return {}
