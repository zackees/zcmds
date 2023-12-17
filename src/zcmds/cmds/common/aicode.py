"""askai - ask openai for help"""

import argparse
import os
import shutil
import sys

from zcmds.cmds.common.openaicfg import create_or_load_config, save_config

try:
    from zcmds.util.chatgpt import ADVANCED_MODEL, FAST_MODEL, SLOW_MODEL
except KeyboardInterrupt:
    # Importing openai stuff can take a while and so if a keyboard interrupt
    # happens during that time then we want to exit immediately rather
    # than throw a cryptic error and stack trace.
    sys.exit(1)


def install_aider_if_missing() -> None:
    """Installs aider to it's own virtual environment using pipx"""
    bin_path = os.path.expanduser("~/.local/bin")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + bin_path
    if shutil.which("aider") is not None:
        return
    print("Installing aider...")
    os.system("pipx install aider-chat")
    assert shutil.which("aider") is not None, "aider not found after install"


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(usage="Ask OpenAI for help with code")
    argparser.add_argument("prompt", help="Prompt to ask OpenAI", nargs="?")
    argparser.add_argument("--set-key", help="Set OpenAI key")

    model_group = argparser.add_mutually_exclusive_group()
    model_group.add_argument(
        "--fast",
        action="store_true",
        default=False,
        help=f"chat gpt 3 turbo: {FAST_MODEL}",
    )
    model_group.add_argument(
        "--slow", action="store_true", default=False, help=f"chat gpt 4: {SLOW_MODEL}"
    )
    model_group.add_argument(
        "--advanced",
        action="store_true",
        default=False,
        help=f"bleeding edge model: {ADVANCED_MODEL}",
    )
    argparser.add_argument(
        "--max-tokens", help="Max tokens to return", type=int, default=None
    )
    model_group.add_argument("--model", default=None)
    return argparser.parse_args()


def cli() -> int:
    args = parse_args()
    config = create_or_load_config()
    if args.set_key:
        config["openai_key"] = args.set_key
        save_config(config)
        config = create_or_load_config()
    model_unspecified = (
        not args.fast and not args.slow and not args.advanced and not args.model
    )
    max_tokens = args.max_tokens
    if args.fast:
        args.model = FAST_MODEL
    if args.model is None:
        if args.slow:
            model = SLOW_MODEL
            if max_tokens is None:
                max_tokens = 4096
        elif args.advanced:
            model = ADVANCED_MODEL
            max_tokens = 128000
        else:
            model = FAST_MODEL
            max_tokens = 4096
    else:
        model = args.model

    install_aider_if_missing()
    openai_key = config.get("openai_key")
    if openai_key is None:
        print("OpenAI key not found, please set one with --set-key")
        return 1
    if not model_unspecified:
        os.environ["AIDER_MODEL"] = model
    else:
        os.environ["AIDER_MODEL"] = ADVANCED_MODEL
    print(f"Starting aider with model {os.environ['AIDER_MODEL']}")
    os.environ["OPENAI_API_KEY"] = openai_key
    return os.system("aider --no-auto-commits")


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
