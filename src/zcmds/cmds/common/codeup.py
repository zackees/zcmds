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

import _thread
import argparse
import logging
import os
import subprocess
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from shutil import which

import openai

# Logger will be configured in main() based on --log flag
logger = logging.getLogger(__name__)

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
    except KeyboardInterrupt:
        logger.info("is_uv_project interrupted by user")
        _thread.interrupt_main()
        return False
    except Exception as e:
        logger.error(f"Error in is_uv_project: {e}")
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


def configure_logging(enable_file_logging: bool) -> None:
    """Configure logging based on whether file logging should be enabled."""
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if enable_file_logging:
        handlers.append(logging.FileHandler("codeup.log"))

    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,  # Override any existing configuration
    )


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
    no_rebase: bool
    strict: bool
    log: bool

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
        assert isinstance(
            self.no_rebase, bool
        ), f"Expected bool, got {type(self.no_rebase)}"
        assert isinstance(self.strict, bool), f"Expected bool, got {type(self.strict)}"
        assert isinstance(self.log, bool), f"Expected bool, got {type(self.log)}"


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
    parser.add_argument(
        "--no-rebase",
        help="Do not attempt to rebase before pushing",
        action="store_true",
    )
    parser.add_argument(
        "--strict",
        help="Fail if auto commit message generation fails",
        action="store_true",
    )
    parser.add_argument(
        "--log",
        help="Enable logging to codeup.log file",
        action="store_true",
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
        no_rebase=tmp.no_rebase,
        strict=tmp.strict,
        log=tmp.log,
    )
    return out


def _publish() -> None:
    publish_script = "upload_package.sh"
    if not os.path.exists(publish_script):
        print(f"Error: {publish_script} does not exist.")
        sys.exit(1)
    _exec("./upload_package.sh", bash=True)


def _get_keyring_api_key() -> str | None:
    """Get OpenAI API key from system keyring/keystore."""
    try:
        import keyring

        api_key = keyring.get_password("zcmds", "openai_api_key")
        return api_key if api_key else None
    except ImportError:
        # keyring not available
        return None
    except KeyboardInterrupt:
        logger.info("_get_keyring_api_key interrupted by user")
        _thread.interrupt_main()
        return None
    except Exception as e:
        logger.error(f"Error accessing keyring: {e}")
        return None


def _generate_ai_commit_message() -> str | None:
    """Generate commit message using git-ai-commit Python API."""
    try:
        # Suppress pkg_resources warnings from ai_commit_msg
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", category=UserWarning, module="ai_commit_msg"
            )
            from ai_commit_msg.core.gen_commit_msg import generate_commit_message
            from ai_commit_msg.services.git_service import GitService

        # Import and use existing OpenAI config system
        try:
            from zcmds.cmds.common.openaicfg import create_or_load_config

            config = create_or_load_config()
            api_key = None

            # Check config file first
            if "openai_key" in config and config["openai_key"]:
                api_key = config["openai_key"]
            # Check keyring/keystore second
            elif _get_keyring_api_key():
                api_key = _get_keyring_api_key()
            # Fall back to environment variable
            elif os.environ.get("OPENAI_API_KEY"):
                api_key = os.environ.get("OPENAI_API_KEY")

            if api_key:
                openai.api_key = api_key
            else:
                print(
                    "Warning: No OpenAI API key found in zcmds config, keyring, or OPENAI_API_KEY environment variable"
                )
                print(
                    "Set key with: imgai --set-key YOUR_KEY or export OPENAI_API_KEY=your_key"
                )
                return None
        except ImportError:
            print("Warning: OpenAI configuration not available")
            return None

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
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", category=UserWarning, module="ai_commit_msg"
            )
            commit_message = generate_commit_message(diff=diff_text, conventional=True)
        return commit_message.strip()

    except ImportError:
        print("Warning: git-ai-commit library not available for AI commit messages")
        print("Install with: pip install git-ai-commit")
        return None
    except KeyboardInterrupt:
        logger.info("_generate_ai_commit_message interrupted by user")
        _thread.interrupt_main()
        return None
    except Exception as e:
        logger.error(f"Failed to generate AI commit message: {e}")
        error_msg = str(e)
        if "OPENAI" in error_msg.upper():
            print(f"Warning: OpenAI API error: {error_msg}")
        else:
            print(f"Warning: Failed to generate AI commit message: {error_msg}")
        return None


def _opencommit_or_prompt_for_commit_message(
    auto_accept: bool, strict: bool = False
) -> None:
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
    elif strict:
        # In strict mode, fail if AI commit generation fails
        print("Error: Failed to generate AI commit message in strict mode")
        print("This may be due to:")
        print("  - OpenAI API issues or rate limiting")
        print("  - Missing or invalid OpenAI API key")
        print("  - Network connectivity problems")
        print(
            "Try running without --strict flag or set API key with: imgai --set-key YOUR_KEY"
        )
        sys.exit(1)

    # Fall back to manual commit message
    msg = input("Commit message: ")
    _exec(f'git commit -m "{msg}"', bash=False)


def _ai_commit_or_prompt_for_commit_message(
    no_autoaccept: bool, message: str | None = None, strict: bool = False
) -> None:
    """Generate commit message using AI or prompt for manual input."""
    if message:
        # Use provided commit message directly
        _exec(f'git commit -m "{message}"', bash=False)
    else:
        # Use AI or interactive commit
        _opencommit_or_prompt_for_commit_message(
            auto_accept=not no_autoaccept, strict=strict
        )


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


def get_main_branch() -> str:
    """Get the main branch name (main, master, etc.)."""
    try:
        # Try to get the default branch from remote
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode == 0:
            return result.stdout.strip().split("/")[-1]
    except KeyboardInterrupt:
        logger.info("get_main_branch interrupted by user")
        _thread.interrupt_main()
        return "main"
    except Exception as e:
        logger.error(f"Error getting main branch: {e}")
        pass

    # Fallback: check common branch names
    for branch in ["main", "master"]:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", f"origin/{branch}"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if result.returncode == 0:
                return branch
        except KeyboardInterrupt:
            logger.info("get_main_branch loop interrupted by user")
            _thread.interrupt_main()
            return "main"
        except Exception as e:
            logger.error(f"Error checking branch {branch}: {e}")
            continue

    return "main"  # Default fallback


def get_current_branch() -> str:
    """Get the current branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def check_rebase_needed(main_branch: str) -> bool:
    """Check if current branch is behind the remote main branch."""
    try:
        remote_hash = subprocess.run(
            ["git", "rev-parse", f"origin/{main_branch}"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        ).stdout.strip()

        # Check if we're behind
        merge_base = subprocess.run(
            ["git", "merge-base", "HEAD", f"origin/{main_branch}"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        ).stdout.strip()

        return merge_base != remote_hash

    except KeyboardInterrupt:
        logger.info("check_rebase_needed interrupted by user")
        _thread.interrupt_main()
        return False
    except Exception as e:
        logger.error(f"Error checking rebase needed: {e}")
        return False


def check_rebase_conflicts(main_branch: str) -> bool:
    """Check if rebase would have conflicts using merge-tree."""
    try:
        # Use git merge-tree to simulate the merge
        result = subprocess.run(
            ["git", "merge-tree", f"origin/{main_branch}", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        # If merge-tree outputs anything, there are conflicts
        return bool(result.stdout.strip())

    except KeyboardInterrupt:
        logger.info("check_rebase_conflicts interrupted by user")
        _thread.interrupt_main()
        return True
    except Exception as e:
        logger.error(f"Error checking rebase conflicts: {e}")
        return True  # Assume conflicts if we can't check


def perform_rebase(main_branch: str) -> bool:
    """Perform the actual rebase. Returns True if successful."""
    try:
        result = subprocess.run(
            ["git", "rebase", f"origin/{main_branch}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode == 0:
            print(f"Successfully rebased onto origin/{main_branch}")
            return True
        else:
            print(f"Rebase failed: {result.stderr}")
            return False

    except KeyboardInterrupt:
        logger.info("perform_rebase interrupted by user")
        _thread.interrupt_main()
        return False
    except Exception as e:
        logger.error(f"Rebase error: {e}")
        print(f"Rebase error: {e}")
        return False


def safe_push() -> bool:
    """Attempt to push safely, never using force push operations."""
    try:
        # First, try a normal push
        print("Attempting to push to remote...")
        result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode == 0:
            print("Successfully pushed to remote")
            return True

        # If normal push failed, check if it's due to non-fast-forward
        stderr_output = result.stderr.lower()

        if "non-fast-forward" in stderr_output or "rejected" in stderr_output:
            print(
                "Push rejected (non-fast-forward). Repository needs to be updated first."
            )
            print(
                "This indicates the remote branch has changes that need to be integrated."
            )
            print(
                "Please run 'git fetch' and 'git rebase origin/<branch>' to update your branch,"
            )
            print(
                "then try pushing again. This ensures all changes are properly integrated."
            )
            return False
        else:
            print(f"Push failed: {result.stderr}")
            return False

    except KeyboardInterrupt:
        logger.info("safe_push interrupted by user")
        _thread.interrupt_main()
        return False
    except Exception as e:
        logger.error(f"Push error: {e}")
        print(f"Push error: {e}")
        return False


def main() -> int:
    """Run git status, lint, test, add, and commit."""

    args = _parse_args()
    configure_logging(args.log)
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
        _ai_commit_or_prompt_for_commit_message(
            args.no_autoaccept, args.message, args.strict
        )

        if not args.no_push:
            # Fetch latest changes from remote
            print("Fetching latest changes from remote...")
            _exec("git fetch", bash=False)

            # Check if rebase is needed and handle it
            if not args.no_rebase:
                main_branch = get_main_branch()
                current_branch = get_current_branch()

                if current_branch != main_branch and check_rebase_needed(main_branch):
                    print(
                        f"Current branch '{current_branch}' is behind origin/{main_branch}"
                    )

                    # Check for potential conflicts
                    if check_rebase_conflicts(main_branch):
                        print(
                            f"Warning: Rebase onto origin/{main_branch} may have conflicts"
                        )
                        proceed = get_answer_yes_or_no(
                            f"Attempt rebase onto origin/{main_branch} anyway?", "n"
                        )
                        if not proceed:
                            print(
                                "Skipping rebase. You may need to resolve conflicts manually."
                            )
                            print(f"Try: git rebase origin/{main_branch}")
                            return 1
                    else:
                        print(f"Rebase onto origin/{main_branch} should be clean")
                        proceed = get_answer_yes_or_no(
                            f"Proceed with rebase onto origin/{main_branch}?", "y"
                        )
                        if not proceed:
                            print("Skipping rebase.")
                            return 1

                    # Perform the rebase
                    if not perform_rebase(main_branch):
                        print(
                            "Rebase failed. Please resolve conflicts manually and try again."
                        )
                        return 1

            # Now attempt the push
            if not safe_push():
                print("Push failed. You may need to resolve conflicts manually.")
                return 1
        if args.publish:
            _publish()
    except KeyboardInterrupt:
        logger.info("codeup main function interrupted by user")
        print("Aborting")
        _thread.interrupt_main()
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in codeup main: {e}")
        print(f"Unexpected error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    main()
