"""aicode - front end for aider"""

import argparse
import os
import shutil
import subprocess
import sys

from zcmds.cmds.common.openaicfg import create_or_load_config, save_config

try:
    from zcmds.util.chatgpt import ADVANCED_MODEL, FAST_MODEL, SLOW_MODEL
except KeyboardInterrupt:
    sys.exit(1)


def install_aider_if_missing() -> None:
    bin_path = os.path.expanduser("~/.local/bin")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + bin_path
    if shutil.which("aider") is not None:
        return
    print("Installing aider...")
    os.system("pipx install aider-chat")
    assert shutil.which("aider") is not None, "aider not found after install"


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(usage="Ask OpenAI for help with code")
    argparser.add_argument(
        "prompt", nargs="*", help="Args to pass onto aider"
    )  # Changed nargs to '*'
    argparser.add_argument("--set-key", help="Set OpenAI key")
    argparser.add_argument("--upgrade", action="store_true", help="Upgrade aider using pipx")

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
    model_group.add_argument("--model", default=None)
    args, unknown_args = argparser.parse_known_args()
    return args, unknown_args


def upgrade_aider() -> None:
    print("Upgrading aider...")
    os.system("pipx upgrade aider-chat")


def get_model(args: argparse.Namespace) -> str:
    if args.fast:
        return FAST_MODEL
    elif args.slow:
        return SLOW_MODEL
    elif args.advanced:
        return ADVANCED_MODEL
    elif args.model is not None:
        return args.model
    else:
        return SLOW_MODEL


def cli() -> int:
    args, unknown_args = parse_args()
    if args.upgrade:
        upgrade_aider()
        return 0
    config = create_or_load_config()
    if args.set_key:
        config["openai_key"] = args.set_key
        save_config(config)
        config = create_or_load_config()
    model = get_model(args)
    install_aider_if_missing()
    openai_key = config.get("openai_key")
    if openai_key is None:
        print("OpenAI key not found, please set one with --set-key")
        return 1
    os.environ["AIDER_MODEL"] = model
    print(f"Starting aider with model {os.environ['AIDER_MODEL']}")
    os.environ["OPENAI_API_KEY"] = openai_key
    return subprocess.call(
        ["aider", "--no-auto-commits"] + args.prompt + unknown_args
    )  # args.prompt and unknown_args are now lists


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
