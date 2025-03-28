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
from dataclasses import dataclass
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


@dataclass
class Args:
    repo: str | None
    no_push: bool
    verbose: bool
    no_test: bool
    no_lint: bool
    publish: bool
    auto_accept_aicommits: bool

    def __post_init__(self) -> None:
        assert isinstance(self.repo, str | None), f"Expected str, got {type(self.repo)}"
        assert isinstance(
            self.no_push, bool
        ), f"Expected bool, got {type(self.no_push)}"
        assert isinstance(
            self.verbose, bool
        ), f"Expected bool, got {type(self.verbose)}"
        assert isinstance(
            self.no_test, bool
        ), f"Expected bool, got {type(self.no_test)}"
        assert isinstance(
            self.no_lint, bool
        ), f"Expected bool, got {type(self.no_lint)}"
        assert isinstance(
            self.publish, bool
        ), f"Expected bool, got {type(self.publish)}"
        assert isinstance(
            self.auto_accept_aicommits, bool
        ), f"Expected bool, got {type(self.auto_accept_aicommits)}"


def _parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="Path to the repo to summarize", nargs="?")
    parser.add_argument(
        "-a",
        "--accept-auto-commit",
        help="Accept auto commit message from ai",
        action="store_true",
    )
    parser.add_argument(
        "--no-push", help="Do not push after successful commit", action="store_true"
    )
    parser.add_argument(
        "--verbose",
        help="Passes the verbose flag to the linter and tester",
        action="store_true",
    )
    parser.add_argument("--publish", "-p", help="Publish the repo", action="store_true")
    parser.add_argument(
        "--no-test", "-nt", help="Do not run tests", action="store_true"
    )
    parser.add_argument("--no-lint", help="Do not run linter", action="store_true")
    tmp = parser.parse_args()

    out: Args = Args(
        repo=tmp.repo,
        no_push=tmp.no_push,
        verbose=tmp.verbose,
        no_test=tmp.no_test,
        no_lint=tmp.no_lint,
        publish=tmp.publish,
        auto_accept_aicommits=tmp.accept_auto_commit,
    )
    return out


def _publish() -> None:
    publish_script = "upload_package.sh"
    if not os.path.exists(publish_script):
        print(f"Error: {publish_script} does not exist.")
        sys.exit(1)
    _exec("bash upload_package.sh")


def _drain_stdin_if_necessary() -> None:
    try:
        if os.name == "posix":
            import select

            while True:
                ready, _, _ = select.select([sys.stdin], [], [], 0)
                if not ready:
                    break
                sys.stdin.read(1)
        elif os.name == "nt":
            import msvcrt

            while msvcrt.kbhit():
                msvcrt.getwch()  # or getch() for bytes
    except EOFError:
        pass
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Error draining stdin: {e}")


def _ai_commit_or_prompt_for_commit_message(auto_accept_aicommits: bool) -> None:
    if which("aicommit2"):
        _drain_stdin_if_necessary()
        cmd = "aicommit2"
        if auto_accept_aicommits:
            cmd += " --confirm"
        _exec(cmd)
    else:
        # Manual commit
        msg = input("Commit message: ")
        msg = f'"{msg}"'
        _exec(f"git commit -m {msg}")


def main() -> int:
    """Run git status, lint, test, add, and commit."""

    args = _parse_args()
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
            _exec("bash lint" + (" --verbose" if verbose else ""))
        if not args.no_test and os.path.exists("./test"):
            _exec("bash test" + (" --verbose" if verbose else ""))
        _exec("git add .")
        _ai_commit_or_prompt_for_commit_message(args.auto_accept_aicommits)
        if not args.no_push:
            _exec("git push")
        if args.publish:
            _publish()
    except KeyboardInterrupt:
        print("Aborting")
        return 1
    return 0


if __name__ == "__main__":
    main()
