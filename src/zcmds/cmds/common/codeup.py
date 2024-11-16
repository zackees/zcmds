"""
Runs:
  * git status
  * if there are not changes then exit 1
  * else
    * if ./lint exists, then run it
    * if ./test exists, then run it
    * git add .
    * aicommit2
"""

import argparse
import os
import sys
import warnings
from pathlib import Path
from shutil import which
from typing import Optional

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

    if not which("aicommit2"):
        warnings.warn(
            "aicommit2 is not installed. Skipping automatic commit message generation."
        )
    return Path(git_dir)


def get_answer_yes_or_no(question: str, default: Optional[str] = None) -> bool:
    """Ask a yes/no question and return the answer."""
    while True:
        answer = input(question + " [y/n]: ").lower().strip()
        if "y" in answer:
            return True
        if "n" in answer:
            return False
        if answer == "" and default is not None:
            return default == "y"
        print("Please answer 'yes' or 'no'.")


def main() -> int:
    """Run git status, lint, test, add, and commit."""
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="Path to the repo to summarize", nargs="?")
    parser.add_argument(
        "--no-push", help="Do not push after successful commit", action="store_true"
    )
    parser.add_argument(
        "--verbose",
        help="Passes the verbose flag to the linter and tester",
        action="store_true",
    )
    parser.add_argument("--no-test", help="Do not run tests", action="store_true")
    parser.add_argument("--no-lint", help="Do not run linter", action="store_true")
    args = parser.parse_args()
    verbose = args.verbose

    git_path = check_environment()
    os.chdir(str(git_path))
    try:
        repo = Repo(".")
        git_status_str = repo.git.status()
        print(git_status_str)
        has_untracked = len(repo.untracked_files) > 0
        if has_untracked:
            print("There are untracked files.")
            answer_yes = get_answer_yes_or_no("Continue?", "y")
            if not answer_yes:
                print("Aborting.")
                return 1
            for untracked_file in repo.untracked_files:
                answer_yes = get_answer_yes_or_no(f"  Add {untracked_file}?", "y")
                if answer_yes:
                    _exec(f"git add {untracked_file}")
                else:
                    print(f"  Skipping {untracked_file}")
        if os.path.exists("./lint") and not args.no_lint:
            _exec("./lint" + (" --verbose" if verbose else ""))
        if not args.no_test and os.path.exists("./test"):
            _exec("./test" + (" --verbose" if verbose else ""))
        _exec("git add .")
        if which("aicommit2"):
            _exec("aicommit2")
        else:
            # Manual commit
            msg = input("Commit message: ")
            msg = f'"{msg}"'
            _exec(f"git commit -m {msg}")
        if not args.no_push:
            _exec("git push")
    except KeyboardInterrupt:
        print("Aborting")
        return 1
    return 0


if __name__ == "__main__":
    main()
