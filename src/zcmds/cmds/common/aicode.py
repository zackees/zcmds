"""aicode - front end for aider"""

import argparse
import atexit
import os
import re
import shutil
import subprocess
import sys
import time
import warnings
from dataclasses import dataclass
from threading import Thread
from typing import Optional, Tuple, Union

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
    rtn = os.system("pipx install aider-chat")
    if rtn != 0:
        assert False, "Failed to install aider"
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


@dataclass
class AiderUpdateResult:
    has_update: bool
    latest_version: str
    current_version: str
    error: Optional[str] = None

    def get_update_msg(self) -> str:
        msg = "\n#######################################\n"
        msg += f"# UPDATE AVAILABLE: {self.current_version} -> {self.latest_version}.\n"
        msg += "# run `aicode --upgrade` to upgrade\n"
        msg += "#######################################\n"
        return msg

    def to_json_data(self) -> dict[str, Union[str, bool, None]]:
        return {
            "has_update": self.has_update,
            "latest_version": self.latest_version,
            "current_version": self.current_version,
            "error": str(self.error) if self.error is not None else None,
        }

    @classmethod
    def from_json(cls, json_data: dict[str, Union[str, bool]]) -> "AiderUpdateResult":
        return AiderUpdateResult(
            has_update=bool(json_data["has_update"]),
            latest_version=str(json_data["latest_version"]),
            current_version=str(json_data["current_version"]),
            error=str(json_data["error"]) if json_data["error"] is not None else None,
        )


def aider_check_update() -> AiderUpdateResult:
    # rtn = os.system("aider --check-update")
    try:
        cp = subprocess.run(
            ["aider", "--check-update"],
            check=False,
            capture_output=True,
            universal_newlines=True,
        )
        if cp.returncode == 0:
            return AiderUpdateResult(False, "", "")
    except Exception:  # pylint: disable=broad-except
        return AiderUpdateResult(False, "", "")
    stdout = cp.stdout.strip()
    lines = stdout.split("\n")
    try:
        current_version: str = extract_version_string(lines[0])
        latest_version: str = extract_version_string(lines[1])
        out = AiderUpdateResult(True, latest_version, current_version)
        # print(out.get_update_msg())
        return out
    except Exception as err:  # pylint: disable=broad-except
        warnings.warn(f"Failed to parse update message: {err}")
        pass
    return AiderUpdateResult(True, "Unknown", "Unknown")


def check_gitignore() -> None:
    needles: dict[str, bool] = {
        ".aider*": False,
        "!.aider.conf.yml": False,
        "!.aiderignore": False,
    }
    if os.path.exists(".gitignore"):
        any_missing = False
        with open(".gitignore", "r") as file:
            content = file.read()
            lines = content.split("\n")
            for needle in needles:
                if needle in lines:
                    needles[needle] = True
                else:
                    any_missing = True
                    print(f".gitignore file does not contain {needle}")
        if any_missing:
            resp = input("Add them? [y/N] ")
            if resp.lower() == "y":
                with open(".gitignore", "a") as file:
                    for needle, found in needles.items():
                        if not found:
                            file.write("\n" + needle)
    else:
        print(".gitignore file does not exist.")


def background_update_task(config: dict) -> None:
    try:
        # Wait for aider to start so that we don't impact startup time.
        # This is really needed for windows because startup is so slow.
        time.sleep(5)
        update_info = aider_check_update()
        if update_info.has_update:
            config["aider_update_info"] = update_info.to_json_data()
            save_config(config)
        else:
            config["aider_update_info"] = {}
            save_config(config)
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass


def cli() -> int:
    check_gitignore()
    args, unknown_args = parse_args()
    config = create_or_load_config()
    if args.upgrade:
        upgrade_aider()
        config["aider_update_info"] = {}  # Purge stale update info
        save_config(config)
        return 0

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

    last_aider_update_info: dict[str, Union[str, bool]] = config.get(
        "aider_update_info", {}
    )
    update_info: Optional[AiderUpdateResult] = None
    if last_aider_update_info:
        try:
            update_info = AiderUpdateResult.from_json(last_aider_update_info)
            if update_info.error:
                warnings.warn(f"Failed to parse update info: {update_info.error}")
                update_info = None
        except Exception as err:  # pylint: disable=broad-except
            warnings.warn(f"Failed to parse update info: {err}")
            update_info = None

    if update_info is not None and update_info.has_update:
        print(update_info.get_update_msg())

    # Note: Aider no longer uses ChatGPT 3.5 turbo by default. Therefore
    # it may soon no longer be necessary to specify the model.
    os.environ["AIDER_MODEL"] = model
    print(f"Starting aider with model {os.environ['AIDER_MODEL']}")
    os.environ["OPENAI_API_KEY"] = openai_key
    cmd_list = ["aider", "--skip-check-update"]
    if args.auto_commit:
        cmd_list.append("--auto-commit")
    else:
        cmd_list.append("--no-auto-commit")
    cmd_list += args.prompt + unknown_args
    print("\nLoading aider:\n  remember to use /help for a list of commands\n")
    # Perform update in the background.
    update_thread = Thread(target=background_update_task, args=(config,))
    update_thread.daemon = True
    update_thread.start()

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
