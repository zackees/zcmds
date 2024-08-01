import os
import subprocess
import sys

from zcmds.util.say import say


def warn(msg: str) -> None:
    """Prints a warning message."""
    print(f"Warning: {msg}", file=sys.stderr)
    say(msg)


def git_status() -> tuple[bool, bool]:
    """Returns (has_changes, has_untracked_files)"""
    status = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
    has_changes = any(
        line.startswith(" M") or line.startswith("M") for line in status.split("\n")
    )
    has_untracked = any(line.startswith("??") for line in status.split("\n"))
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
