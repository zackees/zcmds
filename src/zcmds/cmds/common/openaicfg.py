import argparse
import json
import os
import sys

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


def get_anthropic_api_key() -> str | None:
    """Get Anthropic API key from various sources in order of preference."""
    # 1. Check config file
    config = create_or_load_config()
    if "anthropic_key" in config and config["anthropic_key"]:
        return config["anthropic_key"]

    # 2. Check keyring/keystore
    try:
        import keyring

        api_key = keyring.get_password("zcmds", "anthropic_api_key")
        if api_key:
            return api_key
    except (ImportError, Exception):
        pass

    # 3. Check environment variable
    return os.environ.get("ANTHROPIC_API_KEY")


def get_openai_api_key() -> str | None:
    """Get OpenAI API key from various sources in order of preference."""
    # 1. Check config file
    config = create_or_load_config()
    if "openai_key" in config and config["openai_key"]:
        return config["openai_key"]

    # 2. Check keyring/keystore
    try:
        import keyring

        api_key = keyring.get_password("zcmds", "openai_api_key")
        if api_key:
            return api_key
    except (ImportError, Exception):
        pass

    # 3. Check environment variable
    return os.environ.get("OPENAI_API_KEY")


def _set_key_in_keyring(service: str, key_name: str, api_key: str) -> bool:
    """Set API key in system keyring. Returns True if successful."""
    try:
        import keyring

        keyring.set_password("zcmds", key_name, api_key)
        return True
    except ImportError:
        print("Error: keyring not available. Install with: pip install keyring")
        return False
    except Exception as e:
        print(f"Error storing key in keyring: {e}")
        return False


def _set_key_in_config(key_name: str, api_key: str) -> bool:
    """Set API key in config file. Returns True if successful."""
    try:
        config = create_or_load_config()
        config[key_name] = api_key
        save_config(config)
        return True
    except Exception as e:
        print(f"Error storing key in config: {e}")
        return False


def _show_key_status(key_name: str, source: str, key_value: str | None) -> None:
    """Show masked key status."""
    if key_value:
        masked_key = (
            key_value[:8] + "..." + key_value[-4:] if len(key_value) > 12 else "***"
        )
        print(f"{key_name}: {masked_key} (from {source})")
    else:
        print(f"{key_name}: Not set")


def main() -> int:
    """Main function for openaicfg command - unified AI API key management."""
    parser = argparse.ArgumentParser(
        prog="openaicfg",
        description="Manage OpenAI and Anthropic API keys securely",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  openaicfg --set-key-anthropic sk-ant-...     Set Anthropic key in keyring (secure)
  openaicfg --set-key-openai sk-...           Set OpenAI key in keyring (secure)
  openaicfg --set-key-anthropic sk-ant-... --use-config  Store in config file instead
  openaicfg --show-keys                       Show current key status
        """,
    )

    parser.add_argument(
        "--set-key-anthropic",
        type=str,
        metavar="KEY",
        help="Set Anthropic API key",
    )

    parser.add_argument(
        "--set-key-openai",
        type=str,
        metavar="KEY",
        help="Set OpenAI API key",
    )

    parser.add_argument(
        "--use-config",
        action="store_true",
        help="Store key in config file instead of keyring",
    )

    parser.add_argument(
        "--show-keys",
        action="store_true",
        help="Show current API key status (masked for security)",
    )

    args = parser.parse_args()

    # Show keys status
    if args.show_keys:
        print("API Key Status:")
        print("-" * 40)

        # Check OpenAI key
        openai_key = get_openai_api_key()
        if openai_key == os.environ.get("OPENAI_API_KEY"):
            source = "environment variable"
        else:
            config = create_or_load_config()
            if "openai_key" in config and config["openai_key"] == openai_key:
                source = "config file"
            else:
                source = "keyring"
        _show_key_status("OpenAI", source, openai_key)

        # Check Anthropic key
        anthropic_key = get_anthropic_api_key()
        if anthropic_key == os.environ.get("ANTHROPIC_API_KEY"):
            source = "environment variable"
        else:
            config = create_or_load_config()
            if "anthropic_key" in config and config["anthropic_key"] == anthropic_key:
                source = "config file"
            else:
                source = "keyring"
        _show_key_status("Anthropic", source, anthropic_key)
        return 0

    # Set Anthropic key
    if args.set_key_anthropic:
        if args.use_config:
            if _set_key_in_config("anthropic_key", args.set_key_anthropic):
                print("Anthropic API key stored in config file")
                return 0
            return 1
        else:
            if _set_key_in_keyring(
                "zcmds", "anthropic_api_key", args.set_key_anthropic
            ):
                print("Anthropic API key stored in system keyring")
                return 0
            # Fallback to config if keyring fails
            if _set_key_in_config("anthropic_key", args.set_key_anthropic):
                print("Anthropic API key stored in config file (keyring unavailable)")
                return 0
            return 1

    # Set OpenAI key
    if args.set_key_openai:
        if args.use_config:
            if _set_key_in_config("openai_key", args.set_key_openai):
                print("OpenAI API key stored in config file")
                return 0
            return 1
        else:
            if _set_key_in_keyring("zcmds", "openai_api_key", args.set_key_openai):
                print("OpenAI API key stored in system keyring")
                return 0
            # Fallback to config if keyring fails
            if _set_key_in_config("openai_key", args.set_key_openai):
                print("OpenAI API key stored in config file (keyring unavailable)")
                return 0
            return 1

    # If no specific action, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
