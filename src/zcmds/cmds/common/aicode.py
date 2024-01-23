"""aicode - front end for aider"""

import argparse
import atexit
import os
import re
import shutil
import subprocess
import sys
import warnings
from typing import Tuple

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


class CustomHelpParser(argparse.ArgumentParser):
    def print_help(self):
        # Call the default help message
        super().print_help()
        # Add additional help from the tool you're wrapping
        # print("\n Print aider --help:")
        print("\n\n############ aider --help ############")
        completed_proc = subprocess.run(
            ["aider", "--help"], check=False, capture_output=True
        )
        stdout = completed_proc.stdout.decode("utf-8")
        print(stdout)


def parse_args() -> Tuple[argparse.Namespace, list]:
    argparser = CustomHelpParser(
        usage=(
            "Ask OpenAI for help with code, uses aider-chat on the backend."
            " Any args not listed here are assumed to be for aider and will be passed on to it."
        )
    )
    argparser.add_argument(
        "prompt", nargs="*", help="Args to pass onto aider"
    )  # Changed nargs to '*'
    argparser.add_argument("--set-key", help="Set OpenAI key")
    argparser.add_argument(
        "--upgrade", action="store_true", help="Upgrade aider using pipx"
    )
    argparser.add_argument(
        "--keep", action="store_true", help="Keep chat/input history"
    )
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
    model_group.add_argument(
        "--auto-commit",
        "-a",
        action="store_true",
    )
    model_group.add_argument("--model", default=None)
    args, unknown_args = argparser.parse_known_args()
    return args, unknown_args


def cleanup() -> None:
    files = [
        ".aider.chat.history.md",
        ".aider.input.history",
    ]
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                warnings.warn(f"Failed to remove {file}")


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


def extract_version_string(version_string: str) -> str:
    """
    Extracts "v0.22.0" out of "Newer version v0.22.0 is available. To upgrade, run:"
    """
    match = re.search(r"v?\d+\.\d+\.\d+\S*", version_string)
    if match:
        return match.group()
    raise ValueError(f"Failed to extract version string from {version_string}")


def aider_check_update() -> None:
    # rtn = os.system("aider --check-update")
    try:
        cp = subprocess.run(
            ["aider", "--check-update"],
            check=False,
            capture_output=True,
            universal_newlines=True,
        )
        if cp.returncode == 0:
            return
    except Exception:  # pylint: disable=broad-except
        return
    stdout = cp.stdout.strip()
    lines = stdout.split("\n")
    try:
        current_version = extract_version_string(lines[0])
        latest_version = extract_version_string(lines[1])
        print(
            "\n#######################################\n"
            f"# UPDATE AVAILABLE: {current_version} -> {latest_version}.\n"
            "# run `aicode --upgrade` to upgrade\n"
            "#######################################\n"
        )
        # if input("Upgrade now? [y/N] ").lower() == "y":
        #    upgrade_aider()
        return
    except Exception as err:  # pylint: disable=broad-except
        warnings.warn(f"Failed to parse update message: {err}")
        pass
    print(f"\nUPDATE AVAILABLE: {stdout}, run `aicode --upgrade` to upgrade\n\n")


def cli() -> int:
    args, unknown_args = parse_args()
    if args.upgrade:
        upgrade_aider()
        return 0
    aider_check_update()
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
    cmd_list = ["aider"]
    if args.auto_commit:
        cmd_list.append("--auto-commit")
    else:
        cmd_list.append("--no-auto-commit")
    cmd_list += args.prompt + unknown_args
    print("\nLoading aider:\n  remember to use /help for a list of commands\n")
    rtn = subprocess.call(cmd_list)
    if args.keep:
        return rtn
    atexit.register(cleanup)
    return rtn


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1
    except SystemExit:
        return 1


if __name__ == "__main__":
    sys.exit(main())
