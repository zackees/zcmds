"""
    Normalizes the audio of a video file.
"""

import sys

from zcmds.get_cmds import get_cmds

COMMON = get_cmds(just_names=True)

WIN32 = [
    "cat",
    "cp",
    "du",
    "grep",
    "home",
    "ls",
    "mv",
    "open",
    "rm",
    "which",
    "git-bash",
    "touch",
    "fixvmmem",
    "sudo",
]


def main():
    cmds = COMMON
    cmds = sorted(cmds)
    print("zcmds:")
    print("  common:")
    for cmd in COMMON:
        print(f"    {cmd}")
    if sys.platform == "win32":
        print("  win32:")
        for cmd in sorted(WIN32):
            print(f"    {cmd}")


if __name__ == "__main__":
    main()
