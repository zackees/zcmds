import argparse
import subprocess
import sys
import warnings


def run_git_command(command: list[str]) -> tuple[int, str]:
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
        msg = f"Error running command {' '.join(command)}: {e.stderr}"
        warnings.warn(msg)
        return e.returncode, msg


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pulls from git",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # --all
    parser.add_argument("--all", action="store_true", help="Fetch all branches")
    parser.add_argument(
        "url", nargs="?", default=None, help="URL to set as the remote origin"
    )
    return parser.parse_args()


def fetch_branches(all: bool) -> None:
    cmds_list = ["git", "fetch"]
    if all:
        cmds_list.append("--all")
    run_git_command(cmds_list)


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
    rtn, msg = run_git_command(["git", "checkout", branch])
    if rtn != 0:
        raise RuntimeError(f"Error checking out branch {branch}: {msg}")
    run_git_command(["git", "pull", "--rebase", "origin", branch])


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
    rtn, msg = run_git_command(["git", "remote", "set-url", "origin", url])
    if rtn != 0:
        raise RuntimeError(f"Error setting remote origin URL: {msg}")


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
        pull_rebase_all_branches(["main"])
        print("main branch updated successfully.")
    rtn, msg = run_git_command(["git", "checkout", original_branch])
    if rtn != 0:
        print(f"Error checking out branch {original_branch}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
