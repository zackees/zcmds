"""Configure git."""

import os
import sys

# source: https://jvns.ca/blog/2024/02/16/popular-git-config-options/


def main() -> int:
    """List serial ports."""
    cmds = [
        "git config push.autosetupremote true",
        "git config pull.rebase true",
        # rebase.autostash
        "git config rebase.autoStash true",
        # push.default current
        "git config push.default current",
        # push.default current
        "git config push.default current",
        # init.defaultBranch main
        "git config init.defaultBranch main",
        # help.autocorrect 10
        "git config help.autocorrect 10",
        # diff.algorithm histogram
        "git config diff.algorithm histogram",
        # transfer.fsckobjects = true
        # fetch.fsckobjects = true
        # receive.fsckObjects = true
        "git config transfer.fsckobjects true",
        "git config fetch.fsckobjects true",
        "git config receive.fsckObjects true",
        # blame.ignoreRevsFile .git-blame-ignore-rev
        "git config blame.ignoreRevsFile .git-blame-ignore-rev",
        # branch.sort -committerdate
        "git config branch.sort -committerdate",
    ]
    print("Will install:")
    for cmd in cmds:
        print(f"  {cmd}")

    resp = input("Continue? [y/N] ")
    if resp.lower() != "y":
        print("Aborting.")
        return 1

    for cmd in cmds:
        print(f"Running: {cmd}")
        os.system(cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
