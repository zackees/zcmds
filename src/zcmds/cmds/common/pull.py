import argparse
import subprocess
import sys


def run_git_command(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        msg = f"Error running command {' '.join(command)}: {e.stderr}"
        print(msg, file=sys.stderr)
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pulls from git",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # --all
    parser.add_argument("--all", action="store_true", help="Fetch all branches")
    parser.add_argument("url", nargs="?", default=None, help="URL to set as the remote origin")
    return parser.parse_args()


def fetch_branches(all: bool) -> None:
    print("Fetching all branches...")
    cmds_list = ["git", "fetch"]
    if all:
        cmds_list.append("--all")
    run_git_command(cmds_list)


def get_remote_branches() -> list[str]:
    branches = run_git_command(["git", "branch", "-r"]).splitlines()
    return [
        branch.strip() for branch in branches if "->" not in branch
    ]  # Exclude remote HEAD pointer


def get_local_branches() -> list[str]:
    branches = run_git_command(["git", "branch"]).splitlines()
    return [branch.strip().replace("* ", "") for branch in branches]


def create_missing_local_branches(remote_branches: list[str], local_branches: list[str]) -> None:
    for branch in remote_branches:
        branch_name = branch.replace("origin/", "")
        if branch_name not in local_branches:
            print(f"Creating local branch for {branch}...")
            run_git_command(["git", "branch", "--track", branch_name, branch])


def pull_rebase_branch(branch: str) -> None:
    print(f"Updating {branch} with git pull --rebase...")
    run_git_command(["git", "checkout", branch])
    run_git_command(["git", "pull", "--rebase", "origin", branch])


def pull_rebase_all_branches(local_branches: list[str]) -> None:
    for branch in local_branches:
        pull_rebase_branch(branch)


def set_remote_url(url: str) -> None:
    print(f"Setting remote origin URL to {url}...")
    run_git_command(["git", "remote", "set-url", "origin", url])


def main() -> int:
    args = parse_args()
    if args.url:
        set_remote_url(args.url)
    fetch_branches(all=args.all)

    if args.all:
        print("Fetching all branches completed.")

    if args.all:
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


if __name__ == "__main__":
    sys.exit(main())
