"""
Runs:
  * git status
  * if there are not changes then exit 1
  * else
    * if ./lint exists, then run it
    * if ./test exists, then run it
    * git add .
    * opencommit (oco)
"""

import argparse
import os
import subprocess
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from shutil import which

# Force UTF-8 encoding for proper international character handling
if sys.platform == "win32":
    import codecs

    if sys.stdout.encoding != "utf-8":
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    if sys.stderr.encoding != "utf-8":
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")


def is_uv_project(directory=".") -> bool:
    """
    Detect if the given directory is a uv-managed Python project.

    Args:
        directory (str): Path to the directory to check (default is current directory).

    Returns:
        bool: True if it's a uv project, False otherwise.
    """
    try:
        required_files = ["pyproject.toml", "uv.lock"]
        return all(os.path.isfile(os.path.join(directory, f)) for f in required_files)
    except Exception as e:
        print(f"Error: {e}")
        return False


IS_UV_PROJECT = is_uv_project()

# Example usage
if __name__ == "__main__":
    if is_uv_project():
        print("This is a uv project.")
    else:
        print("This is not a uv project.")


def _to_exec_str(cmd: str, bash: bool) -> str:
    if bash and sys.platform == "win32":
        return f"bash -c '{cmd}'"
    return cmd


def _exec(cmd: str, bash: bool, die=True) -> int:
    print(f"Running: {cmd}")
    cmd = _to_exec_str(cmd, bash)
    rtn = os.system(cmd)
    if rtn != 0:
        print(f"Error: {cmd} returned {rtn}")
        if die:
            sys.exit(1)
    return rtn


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

    if not which("oco"):
        warnings.warn(
            "opencommit (oco) is not installed. Skipping automatic commit message generation."
        )
    return Path(git_dir)


def get_answer_yes_or_no(question: str, default: bool | str = "y") -> bool:
    """Ask a yes/no question and return the answer."""
    while True:
        answer = input(question + " [y/n]: ").lower().strip()
        if "y" in answer:
            return True
        if "n" in answer:
            return False
        if answer == "":
            if isinstance(default, bool):
                return default
            if isinstance(default, str):
                if default.lower() == "y":
                    return True
                elif default.lower() == "n":
                    return False
            return True
        print("Please answer 'yes' or 'no'.")


@dataclass
class Args:
    repo: str | None
    no_push: bool
    verbose: bool
    no_test: bool
    no_lint: bool
    publish: bool
    no_autoaccept: bool
    message: str | None

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
            self.no_autoaccept, bool
        ), f"Expected bool, got {type(self.no_autoaccept)}"
        assert isinstance(
            self.message, str | None
        ), f"Expected str, got {type(self.message)}"


def _parse_args() -> Args:
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
    parser.add_argument("--publish", "-p", help="Publish the repo", action="store_true")
    parser.add_argument(
        "--no-test", "-nt", help="Do not run tests", action="store_true"
    )
    parser.add_argument("--no-lint", help="Do not run linter", action="store_true")
    parser.add_argument(
        "--no-autoaccept",
        "-na",
        help="Do not auto-accept commit messages from AI",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--message",
        help="Commit message (bypasses AI commit generation)",
        type=str,
    )
    tmp = parser.parse_args()

    out: Args = Args(
        repo=tmp.repo,
        no_push=tmp.no_push,
        verbose=tmp.verbose,
        no_test=tmp.no_test,
        no_lint=tmp.no_lint,
        publish=tmp.publish,
        no_autoaccept=tmp.no_autoaccept,
        message=tmp.message,
    )
    return out


def _publish() -> None:
    publish_script = "upload_package.sh"
    if not os.path.exists(publish_script):
        print(f"Error: {publish_script} does not exist.")
        sys.exit(1)
    _exec("./upload_package.sh", bash=True)


def _generate_ai_commit_message() -> str | None:
    """Generate commit message using git-ai-commit Python API."""
    try:
        from ai_commit_msg.core.gen_commit_msg import generate_commit_message
        from ai_commit_msg.services.git_service import GitService

        # Get staged diff using git-ai-commit's GitService
        staged_diff = GitService.get_staged_diff()

        if not staged_diff.stdout.strip():
            # No staged changes, get regular diff
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
            diff_text = result.stdout.strip()
            if not diff_text:
                return None
        else:
            diff_text = staged_diff.stdout

        # Generate commit message using git-ai-commit API
        commit_message = generate_commit_message(diff=diff_text, conventional=True)
        return commit_message.strip()

    except ImportError:
        print("Warning: git-ai-commit library not available for AI commit messages")
        print("Install with: pip install git-ai-commit")
        return None
    except Exception as e:
        print(f"Warning: Failed to generate AI commit message: {e}")
        return None


def _opencommit_or_prompt_for_commit_message(auto_accept: bool) -> None:
    """Generate AI commit message or prompt for manual input."""
    # Try to generate AI commit message first
    ai_message = _generate_ai_commit_message()

    if ai_message:
        print(f"Generated commit message: {ai_message}")

        if auto_accept:
            # Use AI message without confirmation
            _exec(f'git commit -m "{ai_message}"', bash=False)
            return
        else:
            # Ask user to confirm AI message
            use_ai = input("Use this AI-generated message? [y/n]: ").lower().strip()
            if use_ai in ["y", "yes", ""]:
                _exec(f'git commit -m "{ai_message}"', bash=False)
                return

    # Fall back to manual commit message
    msg = input("Commit message: ")
    _exec(f'git commit -m "{msg}"', bash=False)


def _ai_commit_or_prompt_for_commit_message(
    no_autoaccept: bool, message: str | None = None
) -> None:
    """Generate commit message using AI or prompt for manual input."""
    if message:
        # Use provided commit message directly
        _exec(f'git commit -m "{message}"', bash=False)
    else:
        # Use AI or interactive commit
        _opencommit_or_prompt_for_commit_message(auto_accept=not no_autoaccept)


# demo help message


def get_git_status() -> str:
    """Get git status output."""
    result = subprocess.run(
        ["git", "status"], capture_output=True, text=True, check=True, encoding="utf-8"
    )
    return result.stdout


def get_untracked_files() -> list[str]:
    """Get list of untracked files."""
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def main() -> int:
    """Run git status, lint, test, add, and commit."""

    args = _parse_args()
    verbose = args.verbose

    git_path = check_environment()
    os.chdir(str(git_path))
    try:
        git_status_str = get_git_status()
        print(git_status_str)
        untracked_files = get_untracked_files()
        has_untracked = len(untracked_files) > 0
        if has_untracked:
            print("There are untracked files.")
            answer_yes = get_answer_yes_or_no("Continue?", "y")
            if not answer_yes:
                print("Aborting.")
                return 1
            for untracked_file in untracked_files:
                answer_yes = get_answer_yes_or_no(f"  Add {untracked_file}?", "y")
                if answer_yes:
                    _exec(f"git add {untracked_file}", bash=False)
                else:
                    print(f"  Skipping {untracked_file}")
        if os.path.exists("./lint") and not args.no_lint:
            cmd = "./lint" + (" --verbose" if verbose else "")
            # rtn = _exec(cmd, bash=True, die=True)  # Come back to this

            cmd = _to_exec_str(cmd, bash=True)
            uv_resolved_dependencies = True
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
            )
            with proc:
                assert proc.stdout is not None
                for line in proc.stdout:
                    linestr = line.strip()
                    print(linestr)
                    if "No solution found when resolving dependencies" in linestr:
                        uv_resolved_dependencies = False
            proc.wait()
            if proc.returncode != 0:
                print("Error: Linting failed.")
                if uv_resolved_dependencies:
                    sys.exit(1)
                answer_yes = get_answer_yes_or_no(
                    "'uv pip install -e . --refresh'?",
                    "y",
                )
                if not answer_yes:
                    print("Aborting.")
                    sys.exit(1)
                for _ in range(3):
                    refresh_rtn = _exec(
                        "uv pip install -e . --refresh", bash=True, die=False
                    )
                    if refresh_rtn == 0:
                        break
                else:
                    print("Error: uv pip install -e . --refresh failed.")
                    sys.exit(1)
        if not args.no_test and os.path.exists("./test"):
            _exec("./test" + (" --verbose" if verbose else ""), bash=True)
        _exec("git add .", bash=False)
        _ai_commit_or_prompt_for_commit_message(args.no_autoaccept, args.message)
        if not args.no_push:
            _exec("git push", bash=False)
        if args.publish:
            _publish()
    except KeyboardInterrupt:
        print("Aborting")
        return 1
    return 0


if __name__ == "__main__":
    main()
