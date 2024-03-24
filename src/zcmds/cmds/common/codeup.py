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
import warnings
from pathlib import Path
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


def find_git_directory() -> str:
    """Traverse up to 3 levels to find a directory with a .git folder."""
    current_dir = os.getcwd()
    for _ in range(3):
        if os.path.exists(os.path.join(current_dir, ".git")):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if current_dir == parent_dir:
            break
        current_dir = parent_dir
    return ""


def check_environment() -> Path:
    if which("git") is None:
        print("Error: git is not installed.")
        sys.exit(1)
    git_dir = find_git_directory()
    if not git_dir:
        print("Error: .git directory does not exist.")
        sys.exit(1)

    if not which("aicommits"):
        warnings.warn(
            "aicommits is not installed. Skipping automatic commit message generation."
        )
    return Path(git_dir)


def main() -> int:
    """Run git status, lint, test, add, and commit."""
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="Path to the repo to summarize", nargs="?")
    parser.add_argument(
        "--no-push", help="Do not push after successful commit", action="store_true"
    )
    parser.add_argument("--no-test", help="Do not run tests", action="store_true")
    args = parser.parse_args()

    git_path = check_environment()
    os.chdir(str(git_path))
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
        if not args.no_test and os.path.exists("./test"):
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
