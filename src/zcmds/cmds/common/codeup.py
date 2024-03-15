"""
Runs:
  * git status
  * if there are not changes then exit 1
  * else
    * if ./lint exists, then run it
    * if ./test exists, then run it
    * git add .
    * aicommits
"""

import argparse
import os
import sys
from shutil import which

from git import Repo


def _exec(cmd: str) -> None:
    print(f"Running: {cmd}")
    if sys.platform == "win32":
        # we need to run this in the git bash
        cmd = f"bash -c '{cmd}'"
    rtn = os.system(cmd)
    if rtn != 0:
        print(f"Error: {cmd} returned {rtn}")
        exit(1)


def check_environment() -> None:
    if which("git") is None:
        print("Error: git is not installed.")
        sys.exit(1)
    if not os.path.exists(".git"):
        print("Error: .git directory does not exist.")
        sys.exit(1)
    if not os.path.exists("lint"):
        print("Error: lint script does not exist.")
        sys.exit(1)
    if not os.path.exists("test"):
        print("Error: test script does not exist.")
        sys.exit(1)
    if not which("aicommits"):
        print("Error: aicommits script does not exist.")
        sys.exit(1)


def main() -> int:
    """Run git status, lint, test, add, and commit."""
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="Path to the repo to summarize", nargs="?")
    parser.add_argument(
        "--no-push", help="Do not push after successful commit", action="store_true"
    )
    args = parser.parse_args()

    check_environment()
    try:
        repo = Repo(".")
        git_status_str = repo.git.status()
        print(git_status_str)
        has_untracked = len(repo.untracked_files) > 0
        if has_untracked:
            print("There are untracked files.")
            answer = input("Continue? [y/N] ")
            if answer.lower() != "y":
                print("Aborting.")
                return 1
        if os.path.exists("./lint"):
            _exec("./lint")
        if os.path.exists("./test"):
            _exec("./test")
        _exec("git add .")
        if which("aicommits"):
            _exec("aicommits")
        else:
            # Manual commit
            msg = input("Commit message: ")
            _exec(f"git commit -m {msg}")
        if not args.no_push:
            _exec("push")
    except KeyboardInterrupt:
        print("Aborting")
        return 1
    return 0


if __name__ == "__main__":
    main()
