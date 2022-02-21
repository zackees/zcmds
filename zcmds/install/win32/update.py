# pylint: skip-file
"""
    Installation/Update script for win32.
"""

import os
import shutil
import sys
from typing import List

from zcmds.paths import BIN_DIR, CMD_COMMON_DIR, CMD_WIN32_DIR
from zcmds.util import win32_path_manip

SELF_DIR = os.path.abspath(os.path.dirname(__file__))


def gen_win_cmds() -> None:
    """Generates windows commands."""
    common_cmds = os.listdir(CMD_COMMON_DIR)
    if "__init__.py" in common_cmds:
        common_cmds.remove("__init__.py")
    common_cmds = [
        os.path.abspath(os.path.join(CMD_COMMON_DIR, f)) for f in common_cmds
    ]
    win32_cmds = [
        os.path.abspath(os.path.join(CMD_WIN32_DIR, f)) for f in os.listdir(CMD_WIN32_DIR)
    ]
    all_cmds = common_cmds + win32_cmds
    all_cmds = [cmd for cmd in all_cmds if cmd.endswith(".py") or cmd.endswith(".bat")]
    shutil.rmtree(BIN_DIR, ignore_errors=True)
    os.makedirs(BIN_DIR, exist_ok=True)
    cmd_set = set([])
    for cmd in all_cmds:
        if cmd in cmd_set:
            sys.stderr.write(
                f"Warning, duplicate found for {os.path.basename(cmd)}, skipping."
            )
        else:
            cmd_set.add(cmd)
        if cmd.endswith(".py"):
            cmd_name = os.path.basename(cmd)
            out_cmd = os.path.join(BIN_DIR, cmd_name)[0:-3] + ".bat"  # swap .py -> .bat
            with open(
                out_cmd, encoding="utf-8", mode="wt"
            ) as f:  # pylint: disable=invalid-name
                f.write(f"python {cmd} %1 %2 %3 %4 %5 %6 %7 %8 %9\n")

        elif cmd.endswith(".bat"):
            cmd_name = os.path.basename(cmd)
            out_cmd = os.path.join(BIN_DIR, cmd_name)
            print(f"copying command {cmd} -> {out_cmd}")
            shutil.copy(cmd, out_cmd)
        else:
            print(f"Unexpected command type: {cmd}")


def is_cmd_path_installed() -> bool:
    """Detects if the path is already installed."""
    all_paths: List[str] = win32_path_manip.read_user_path()
    return BIN_DIR in all_paths


def add_cmds_to_path() -> None:
    """Adds commands to the Win32 path, if it's not already installed."""
    if is_cmd_path_installed():
        print(f"Already found {BIN_DIR} in %PATH%")
        return
    print(f"\nDid not found {BIN_DIR} in %PATH%, adding...\n")
    win32_path_manip.append_user_path_if_not_exist(BIN_DIR)


def main():
    """Entry point."""
    gen_win_cmds()
    add_cmds_to_path()


if __name__ == "__main__":
    main()
