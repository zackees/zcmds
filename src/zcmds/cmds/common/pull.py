import argparse
import subprocess
import sys
import warnings


def run_git_command(command: list[str], capture_output: bool = True) -> tuple[int, str]:
    """
    Run a git command.

    Args:
        command: The git command to run as a list of strings
        capture_output: If True, capture and return output. If False, stream to terminal.

    Returns:
        Tuple of (return_code, output_message)
    """
    try:
        if capture_output:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return 0, result.stdout
        else:
            # Stream output directly to terminal
            result = subprocess.run(command, check=True)
            return 0, ""
    except subprocess.CalledProcessError as e:
        if capture_output:
            msg = f"Error running command {' '.join(command)}: {e.stderr}"
            warnings.warn(msg)
            return e.returncode, msg
        else:
            # Error was already printed to stderr
            return e.returncode, f"Command failed: {' '.join(command)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pulls from git",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # --all
    parser.add_argument("--all", action="store_true", help="Fetch all branches")
    parser.add_argument(
        "--recurse-submodules",
        action="store_true",
        help="Recursively update submodules without prompting",
    )
    parser.add_argument(
        "--no-submodules",
        action="store_true",
        help="Skip submodule updates without prompting",
    )
    parser.add_argument(
        "url", nargs="?", default=None, help="URL to set as the remote origin"
    )
    return parser.parse_args()


def fetch_branches(all: bool) -> None:
    cmds_list = ["git", "fetch"]
    if all:
        cmds_list.append("--all")
    run_git_command(cmds_list, capture_output=False)


def get_remote_branches() -> list[str]:
    rtn, msg = run_git_command(["git", "branch", "-r"])
    if rtn != 0:
        raise RuntimeError(f"Error fetching remote branches: {msg}")
    branches = msg.splitlines()
    return [
        branch.strip() for branch in branches if "->" not in branch
    ]  # Exclude remote HEAD pointer


def get_local_branches() -> list[str]:
    rtn, msg = run_git_command(["git", "branch"])
    if rtn != 0:
        raise RuntimeError("Error fetching local branches")
    branches = msg.splitlines()
    return [branch.strip().replace("* ", "") for branch in branches]


def create_missing_local_branches(
    remote_branches: list[str], local_branches: list[str]
) -> None:
    for branch in remote_branches:
        branch_name = branch.replace("origin/", "")
        if branch_name not in local_branches:
            print(f"Creating local branch for {branch}...")
            rtn, msg = run_git_command(
                ["git", "branch", "--track", branch_name, branch]
            )
            if rtn != 0:
                raise RuntimeError(f"Error creating local branch: {msg}")


def pull_rebase_branch(branch: str) -> None:
    print(f"Updating {branch} with git pull --rebase...")
    rtn, msg = run_git_command(["git", "checkout", branch], capture_output=False)
    if rtn != 0:
        raise RuntimeError(f"Error checking out branch {branch}: {msg}")
    run_git_command(["git", "pull", "--rebase", "origin", branch], capture_output=False)


def get_current_branch() -> str:
    rtn, msg = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if rtn != 0:
        raise RuntimeError(f"Error getting current branch: {msg}")
    msg = msg.strip()
    return msg


def pull_rebase_all_branches(local_branches: list[str]) -> None:
    for branch in local_branches:
        pull_rebase_branch(branch)


def set_remote_url(url: str) -> None:
    print(f"Setting remote origin URL to {url}...")
    rtn, msg = run_git_command(
        ["git", "remote", "set-url", "origin", url], capture_output=False
    )
    if rtn != 0:
        raise RuntimeError(f"Error setting remote origin URL: {msg}")


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


def has_submodules() -> bool:
    """Check if the repository has any submodules."""
    import os

    # Check if .gitmodules exists
    if os.path.exists(".gitmodules"):
        return True
    return False


def submodules_need_update() -> bool:
    """
    Check if submodules have updates available on the remote.

    This checks if:
    1. The parent repo has newer submodule commit references (after pull)
    2. Submodules are not initialized yet

    Returns:
        True if submodules need updating, False otherwise
    """
    # First check if there are any submodules at all
    if not has_submodules():
        return False

    # Check submodule status
    # Status indicators:
    # '-' = submodule is not initialized
    # '+' = currently checked out commit doesn't match what's recorded in parent
    # 'U' = merge conflicts
    # ' ' = submodule is up to date
    rtn, msg = run_git_command(["git", "submodule", "status"])

    if rtn != 0:
        # If we can't determine status, assume no updates needed
        return False

    # If any submodule is uninitialized or out of sync, it needs updating
    for line in msg.splitlines():
        if not line:
            continue
        # Check the first character (status indicator)
        first_char = line[0] if line else " "
        if first_char in ["-", "+", "U"]:
            return True

    return False


def prompt_submodule_update() -> str:
    """
    Prompt the user whether to update submodules.

    Returns:
        'no': Don't update submodules
        'recursive': Update submodules recursively
        'non-recursive': Update submodules non-recursively
    """
    while True:
        try:
            print("\nSubmodules need updating. How would you like to proceed?")
            print("  [1] No - skip submodule updates")
            print("  [2] Yes - update recursively (recommended)")
            print("  [3] Yes - update non-recursively (top-level only)")
            response = input("Choice [1]: ").strip().lower()

            # Default to option 1 (No) if no input
            if response == "" or response == "1":
                return "no"
            elif response == "2":
                return "recursive"
            elif response == "3":
                return "non-recursive"
            else:
                print("Please enter 1, 2, or 3")
        except (EOFError, KeyboardInterrupt):
            # Handle non-interactive environments or user interrupt
            print()
            return "no"


def update_submodules(recursive: bool = True) -> None:
    """Update submodules.

    Args:
        recursive: If True, update recursively. If False, only update top-level submodules.
    """
    if recursive:
        print("Updating submodules recursively...")
        rtn, msg = run_git_command(
            ["git", "submodule", "update", "--init", "--recursive", "--remote"],
            capture_output=False,
        )
    else:
        print("Updating submodules (top-level only)...")
        rtn, msg = run_git_command(
            ["git", "submodule", "update", "--init", "--remote"], capture_output=False
        )

    if rtn != 0:
        warnings.warn(f"Error updating submodules: {msg}")
    else:
        print("Submodules updated successfully.")


def main() -> int:
    args = parse_args()
    original_branch = get_current_branch()
    if args.url:
        set_remote_url(args.url)
    fetch_branches(all=args.all)

    if args.all:
        print("Fetching all branches completed.")
        remote_branches = get_remote_branches()
        local_branches = get_local_branches()
        create_missing_local_branches(remote_branches, local_branches)
        # Update local branches list after branch creation
        local_branches = get_local_branches()
        pull_rebase_all_branches(local_branches)
        print("All branches updated successfully.")
    else:
        default_branch = get_default_branch()
        pull_rebase_all_branches([default_branch])
        print(f"{default_branch} branch updated successfully.")
    rtn, msg = run_git_command(
        ["git", "checkout", original_branch], capture_output=False
    )
    if rtn != 0:
        print(f"Error checking out branch {original_branch}: {msg}")
        return 1

    # Handle submodule updates
    submodule_mode = "no"

    if args.recurse_submodules:
        # Explicitly requested recursive submodule update
        submodule_mode = "recursive"
    elif not args.no_submodules and submodules_need_update():
        # Only prompt if submodules exist AND need updating
        # This checks after the pull to see if submodule refs changed
        submodule_mode = prompt_submodule_update()

    if submodule_mode == "recursive":
        update_submodules(recursive=True)
    elif submodule_mode == "non-recursive":
        update_submodules(recursive=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
