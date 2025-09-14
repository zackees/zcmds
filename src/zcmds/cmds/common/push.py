import os
import subprocess
import sys
import warnings

from zcmds.util.say import say


def warn(msg: str) -> None:
    """Prints a warning message."""
    print(f"Warning: {msg}", file=sys.stderr)
    say(msg)


def run_git_command(command: list[str]) -> tuple[int, str]:
    """Run a git command and return (exit_code, output)"""
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return 0, result.stdout
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stderr


def get_default_branch() -> str:
    """Get the default branch name from the remote origin."""
    # First try to get the remote HEAD reference
    rtn, msg = run_git_command(["git", "symbolic-ref", "refs/remotes/origin/HEAD"])
    if rtn == 0:
        # Extract branch name from refs/remotes/origin/main format
        branch_ref = msg.strip()
        if branch_ref.startswith("refs/remotes/origin/"):
            return branch_ref.replace("refs/remotes/origin/", "")

    # If that fails, try to get it from remote show origin
    rtn, msg = run_git_command(["git", "remote", "show", "origin"])
    if rtn == 0:
        for line in msg.splitlines():
            line = line.strip()
            if line.startswith("HEAD branch:"):
                return line.split(":", 1)[1].strip()

    # If all else fails, try common default branch names
    for branch_name in ["main", "master"]:
        rtn, _ = run_git_command(
            ["git", "rev-parse", "--verify", f"origin/{branch_name}"]
        )
        if rtn == 0:
            return branch_name

    # Last resort: return "main" as fallback
    warnings.warn("Could not determine default branch, falling back to 'main'")
    return "main"


def git_status() -> tuple[bool, bool]:
    """Returns (has_changes, has_untracked_files)"""
    status = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
    if not status:
        return False, False

    has_changes = any(
        line.startswith(" M") or line.startswith("M")
        for line in status.split("\n")
        if line.strip()
    )
    has_untracked = any(
        line.startswith("??") for line in status.split("\n") if line.strip()
    )
    return has_changes, has_untracked


def get_current_branch() -> str:
    """Returns the name of the current git branch."""
    return (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .decode()
        .strip()
    )


def main() -> int:
    has_changes, has_untracked = git_status()
    if has_changes:
        warn(
            "Push failed: there are uncommitted changes that need to be committed or stashed first."
        )
        return 1
    if has_untracked:
        warn(
            "Push failed: there are untracked files that need to be committed or removed first."
        )
        return 1

    current_branch = get_current_branch()

    # Fetch the repo
    os.system("git fetch")

    # Push to origin
    push_result = os.system(f"git push origin {current_branch}")
    if push_result != 0:
        if (
            "no upstream branch"
            in subprocess.getoutput(f"git push origin {current_branch}").lower()
        ):
            warn(
                f"No upstream branch found for {current_branch}. Push failed, but returning 0 as requested."
            )
            return 0
        else:
            warn(f"Push failed with exit code {push_result}")
            return 1

    print(f"Successfully pushed to origin/{current_branch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
