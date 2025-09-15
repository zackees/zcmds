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


def _safe_git_commit(message: str) -> int:
    """Safely execute git commit with proper UTF-8 encoding."""
    try:
        print(f'Running: git commit -m "{message}"')
        result = subprocess.run(
            ["git", "commit", "-m", message],
            encoding="utf-8",
            errors="replace",
            text=True,
            capture_output=False,  # Let output go to console directly
        )
        if result.returncode != 0:
            print(f"Error: git commit returned {result.returncode}")
        return result.returncode
    except KeyboardInterrupt:
        logger.info("_safe_git_commit interrupted by user")
        _thread.interrupt_main()
        return 130
    except Exception as e:
        logger.error(f"Error in _safe_git_commit: {e}")
        print(f"Error executing git commit: {e}", file=sys.stderr)
        return 1


def _exec(cmd: str, bash: bool, die=True) -> int:
    print(f"Running: {cmd}")
    cmd = _to_exec_str(cmd, bash)

    try:
        # Use subprocess.run instead of os.system for better encoding control
        result = subprocess.run(
            cmd,
            shell=True,
            encoding="utf-8",
            errors="replace",
            text=True,
            capture_output=False,  # Let output go to console directly
        )
        rtn = result.returncode
    except KeyboardInterrupt:
        logger.info("_exec interrupted by user")
        _thread.interrupt_main()
        return 130
    except Exception as e:
        logger.error(f"Error in _exec: {e}")
        print(f"Error executing command: {e}", file=sys.stderr)
        rtn = 1

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
        level=logging.INFO,  # Changed from ERROR to INFO for more detailed logging
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
    no_interactive: bool
    log: bool
    just_ai_commit: bool

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
        assert isinstance(
            self.no_interactive, bool
        ), f"Expected bool, got {type(self.no_interactive)}"
        assert isinstance(self.log, bool), f"Expected bool, got {type(self.log)}"
        assert isinstance(
            self.just_ai_commit, bool
        ), f"Expected bool, got {type(self.just_ai_commit)}"


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
        "--no-interactive",
        help="Fail if auto commit message generation fails (non-interactive mode)",
        action="store_true",
    )
    parser.add_argument(
        "--log",
        help="Enable logging to codeup.log file",
        action="store_true",
    )
    parser.add_argument(
        "--just-ai-commit",
        help="Skip linting and testing, just run the automatic AI commit generator",
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
        no_interactive=tmp.no_interactive,
        log=tmp.log,
        just_ai_commit=tmp.just_ai_commit,
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
            key_source = None

            # Check config file first
            if "openai_key" in config and config["openai_key"]:
                api_key = config["openai_key"]
                key_source = "zcmds config"
                logger.info(f"Using OpenAI API key from {key_source}")
            # Check keyring/keystore second
            elif _get_keyring_api_key():
                api_key = _get_keyring_api_key()
                key_source = "keyring"
                logger.info(f"Using OpenAI API key from {key_source}")
            # Fall back to environment variable
            elif os.environ.get("OPENAI_API_KEY"):
                api_key = os.environ.get("OPENAI_API_KEY")
                key_source = "environment variable"
                logger.info(f"Using OpenAI API key from {key_source}")

            if api_key:
                # Set the API key for both openai and git-ai-commit
                openai.api_key = api_key
                os.environ["OPENAI_API_KEY"] = api_key
                logger.info(
                    f"API key configured from {key_source}, length: {len(api_key)}"
                )
            else:
                logger.warning("No OpenAI API key found in any source")
                print(
                    "Warning: No OpenAI API key found in zcmds config, keyring, or OPENAI_API_KEY environment variable"
                )
                print(
                    "Set key with: imgai --set-key YOUR_KEY or export OPENAI_API_KEY=your_key"
                )
                return None
        except ImportError as e:
            logger.error(f"Import error in OpenAI config: {e}")
            print("Warning: OpenAI configuration not available")
            return None

        # Get staged diff using git-ai-commit's GitService
        logger.info("Getting git diff for commit message generation")
        staged_diff = GitService.get_staged_diff()

        if not staged_diff.stdout.strip():
            # No staged changes, get regular diff
            logger.info("No staged changes, getting regular diff")
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
            diff_text = result.stdout.strip()
            if not diff_text:
                logger.warning("No changes found in git diff")
                return None
        else:
            diff_text = staged_diff.stdout
            logger.info(f"Got staged diff, length: {len(diff_text)}")

        # Generate commit message using git-ai-commit API
        logger.info("Calling generate_commit_message from git-ai-commit")
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", category=UserWarning, module="ai_commit_msg"
            )
            commit_message = generate_commit_message(diff=diff_text, conventional=True)

        if commit_message is None:
            logger.warning("AI commit message generation returned None")
            print("Warning: AI commit message generation returned None")
            return None

        logger.info(f"Successfully generated commit message: {commit_message[:50]}...")
        return commit_message.strip()

    except ImportError as e:
        logger.error(f"ImportError in _generate_ai_commit_message: {e}")
        print("Warning: git-ai-commit library not available for AI commit messages")
        print("Install with: pip install git-ai-commit")
        return None
    except KeyboardInterrupt:
        logger.info("_generate_ai_commit_message interrupted by user")
        _thread.interrupt_main()
        return None
    except Exception as e:
        logger.error(f"Failed to generate AI commit message: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception args: {e.args}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")

        error_msg = str(e)
        print("Error: AI commit message generation failed")
        print(f"Exception: {type(e).__name__}: {error_msg}")
        print("Full traceback:")
        print(traceback.format_exc())

        if "OPENAI" in error_msg.upper():
            print("This appears to be an OpenAI API error.")

        return None


def _opencommit_or_prompt_for_commit_message(
    auto_accept: bool, no_interactive: bool = False
) -> None:
    """Generate AI commit message or prompt for manual input."""
    # Try to generate AI commit message first
    ai_message = _generate_ai_commit_message()

    if ai_message:
        print(f"Generated commit message: {ai_message}")

        if auto_accept:
            # Use AI message without confirmation
            _safe_git_commit(ai_message)
            return
        else:
            # Ask user to confirm AI message
            use_ai = input("Use this AI-generated message? [y/n]: ").lower().strip()
            if use_ai in ["y", "yes", ""]:
                _safe_git_commit(ai_message)
                return
    elif no_interactive:
        # In non-interactive mode, fail if AI commit generation fails
        print("Error: Failed to generate AI commit message in non-interactive mode")
        print("This may be due to:")
        print("  - OpenAI API issues or rate limiting")
        print("  - Missing or invalid OpenAI API key")
        print("  - Network connectivity problems")
        print("Solutions:")
        print("  - Run in interactive mode: codeup (without --no-interactive)")
        print("  - Set API key via environment: export OPENAI_API_KEY=your_key")
        print("  - Set API key via imgai: imgai --set-key YOUR_KEY")
        print("  - Set API key via Python config:")
        print(
            "    python -c \"from zcmds.cmds.common.openaicfg import save_config; save_config({'openai_key': 'your_key'})\""
        )
        sys.exit(1)

    # Fall back to manual commit message
    msg = input("Commit message: ")
    _safe_git_commit(msg)


def _ai_commit_or_prompt_for_commit_message(
    no_autoaccept: bool, message: str | None = None, no_interactive: bool = False
) -> None:
    """Generate commit message using AI or prompt for manual input."""
    if message:
        # Use provided commit message directly
        _safe_git_commit(message)
    else:
        # Use AI or interactive commit
        _opencommit_or_prompt_for_commit_message(
            auto_accept=not no_autoaccept, no_interactive=no_interactive
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


def safe_rebase_try() -> bool:
    """Attempt a safe rebase if no conflicts would occur. Returns True if successful or no rebase needed."""
    try:
        # Get the main branch
        main_branch = get_main_branch()
        current_branch = get_current_branch()

        # If we're on the main branch, no rebase needed
        if current_branch == main_branch:
            return True

        # Check if rebase is needed
        if not check_rebase_needed(main_branch):
            print(f"Branch is already up to date with origin/{main_branch}")
            return True

        # Check for conflicts before attempting rebase
        if check_rebase_conflicts(main_branch):
            print(f"Cannot safely rebase: conflicts detected with origin/{main_branch}")
            print(
                "Remote repository has conflicting changes and must be manually rebased."
            )
            print(f"Run: git rebase origin/{main_branch}")
            print("Then resolve any conflicts manually.")
            return False

        # Safe to rebase - no conflicts detected
        print(f"Attempting safe rebase onto origin/{main_branch}...")
        if perform_rebase(main_branch):
            print(f"Successfully rebased onto origin/{main_branch}")
            return True
        else:
            print("Rebase failed unexpectedly")
            return False

    except KeyboardInterrupt:
        logger.info("safe_rebase_try interrupted by user")
        _thread.interrupt_main()
        return False
    except Exception as e:
        logger.error(f"Error in safe_rebase_try: {e}")
        print(f"Error during safe rebase attempt: {e}")
        return False


def safe_push() -> bool:
    """Attempt to push safely, with automatic rebase if safe to do so."""
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

            # Attempt safe rebase if possible
            if safe_rebase_try():
                # Rebase succeeded, try push again
                print("Rebase successful, attempting push again...")
                result = subprocess.run(
                    ["git", "push"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )

                if result.returncode == 0:
                    print("Successfully pushed to remote after rebase")
                    return True
                else:
                    print(f"Push failed after rebase: {result.stderr}")
                    return False
            else:
                # Rebase failed or not safe, provide manual instructions
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

    # Force UTF-8 encoding for all subprocess operations on Windows
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if sys.platform == "win32":
        os.environ["PYTHONLEGACYWINDOWSSTDIO"] = "0"

    args = _parse_args()
    configure_logging(args.log)
    verbose = args.verbose

    git_path = check_environment()
    os.chdir(str(git_path))

    # Handle --just-ai-commit flag
    if args.just_ai_commit:
        try:
            # Just run the AI commit workflow
            _exec("git add .", bash=False)
            _ai_commit_or_prompt_for_commit_message(
                args.no_autoaccept, args.message, no_interactive=True
            )
            return 0
        except KeyboardInterrupt:
            logger.info("just-ai-commit interrupted by user")
            print("Aborting")
            _thread.interrupt_main()
            return 1
        except Exception as e:
            logger.error(f"Unexpected error in just-ai-commit: {e}")
            print(f"Unexpected error: {e}")
            return 1

    try:
        git_status_str = get_git_status()
        print(git_status_str)
        untracked_files = get_untracked_files()
        has_untracked = len(untracked_files) > 0
        if has_untracked:
            print("There are untracked files.")
            if args.no_interactive:
                # In non-interactive mode, automatically add all untracked files
                print("Non-interactive mode: automatically adding all untracked files.")
                for untracked_file in untracked_files:
                    print(f"  Adding {untracked_file}")
                    _exec(f"git add {untracked_file}", bash=False)
            else:
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
                errors="replace",  # Replace unmappable characters
                bufsize=1,  # Line buffered
            )

            # Stream output with 60-second timeout between lines
            import time

            with proc:
                assert proc.stdout is not None
                timeout_duration = 60  # 60 seconds of silence before timeout
                last_output_time = time.time()

                while True:
                    # Check if process has finished
                    if proc.poll() is not None:
                        break

                    # Check for timeout (no output for 60 seconds)
                    if time.time() - last_output_time > timeout_duration:
                        print(
                            f"Warning: Lint process timed out after {timeout_duration} seconds of no output"
                        )
                        proc.kill()
                        proc.wait()
                        print("Error: Linting process hung and was terminated.")
                        sys.exit(1)

                    # Try to read a line
                    try:
                        line = proc.stdout.readline()
                        if line:
                            # Since we're using text=True, line is already a string
                            linestr = line.strip()
                            print(linestr)
                            last_output_time = time.time()  # Reset timeout on output
                            if (
                                "No solution found when resolving dependencies"
                                in linestr
                            ):
                                uv_resolved_dependencies = False
                        else:
                            # No line available, sleep briefly and continue
                            time.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Error reading lint output: {e}")
                        break

            proc.wait()
            if proc.returncode != 0:
                print("Error: Linting failed.")
                if uv_resolved_dependencies:
                    sys.exit(1)
                if args.no_interactive:
                    print(
                        "Non-interactive mode: automatically running 'uv pip install -e . --refresh'"
                    )
                    answer_yes = True
                else:
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
            test_cmd = "./test" + (" --verbose" if verbose else "")
            test_cmd = _to_exec_str(test_cmd, bash=True)

            print(f"Running: {test_cmd}")
            test_proc = subprocess.Popen(
                test_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",  # Replace unmappable characters
                bufsize=1,  # Line buffered
            )

            # Stream test output with 60-second timeout between lines
            with test_proc:
                assert test_proc.stdout is not None
                timeout_duration = 60  # 60 seconds of silence before timeout
                last_output_time = time.time()

                while True:
                    # Check if process has finished
                    if test_proc.poll() is not None:
                        break

                    # Check for timeout (no output for 60 seconds)
                    if time.time() - last_output_time > timeout_duration:
                        print(
                            f"Warning: Test process timed out after {timeout_duration} seconds of no output"
                        )
                        test_proc.kill()
                        test_proc.wait()
                        print("Error: Test process hung and was terminated.")
                        sys.exit(1)

                    # Try to read a line
                    try:
                        line = test_proc.stdout.readline()
                        if line:
                            # Since we're using text=True, line is already a string
                            linestr = line.strip()
                            print(linestr)
                            last_output_time = time.time()  # Reset timeout on output
                        else:
                            # No line available, sleep briefly and continue
                            time.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Error reading test output: {e}")
                        break

            test_proc.wait()
            if test_proc.returncode != 0:
                print("Error: Tests failed.")
                sys.exit(1)
        _exec("git add .", bash=False)
        _ai_commit_or_prompt_for_commit_message(
            args.no_autoaccept, args.message, args.no_interactive
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
                        if args.no_interactive:
                            print(
                                "Non-interactive mode: skipping rebase due to potential conflicts"
                            )
                            print(
                                f"You may need to resolve conflicts manually with: git rebase origin/{main_branch}"
                            )
                            return 1
                        else:
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
                        if args.no_interactive:
                            print(
                                f"Non-interactive mode: automatically proceeding with rebase onto origin/{main_branch}"
                            )
                            proceed = True
                        else:
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
