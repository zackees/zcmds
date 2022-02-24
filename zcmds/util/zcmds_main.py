# pylint: skip-file

"""
    Main entry point into the zcmds console program.
"""

import os
import sys

from zcmds.install.update import main as update_main

SELF_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(SELF_DIR, ".."))
BIN_DIR = os.path.join(BASE_DIR, "bin")


def main():
    first_run = not os.path.isdir(BIN_DIR)
    os.makedirs(BIN_DIR, exist_ok=True)
    if "update" in sys.argv or first_run:
        update_main()
    cmds = os.listdir(BIN_DIR)
    if sys.platform == "win32":
        cmds = [os.path.splitext(c)[0] for c in cmds if c.endswith(".bat") or c.endswith(".exe")]
    cmds.append("ytclip")
    cmds = list(set(cmds))
    if "update" in cmds:
        cmds.remove("update")
    cmds.append("zcmds update")
    cmds.append("zcmds_install")
    cmds.sort()
    print(f"BIN_DIR: {BIN_DIR}:\nCommands:\n  " + "\n  ".join(cmds))
    return


if __name__ == "__main__":
    main()
