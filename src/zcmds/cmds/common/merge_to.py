import argparse
import sys

from git import Repo


def git_has_uncommitted_changes_or_untracked_files() -> bool:
    """Returns True if git has uncommitted changes or untracked files."""
    try:
        from git import Repo  # type: ignore
    except ImportError:
        return False
    repo = Repo(".")
    return repo.is_dirty() or len(repo.untracked_files) > 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Switches to another branch, then merges the current branch into it, then switches back to the original branch.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "branch",
        help="Branch to switch to. If the branch does not exist, it will be created.",
    )
    return parser.parse_args()


def main() -> int:
    if git_has_uncommitted_changes_or_untracked_files():
        print("Please commit or stash your changes before running this script.")
        return 1
    args = parse_args()
    branch = args.branch
    repo = Repo(".")
    original_branch = repo.active_branch
    print(f"checkout {branch}")
    repo.git.checkout(branch)
    print(f"merge {original_branch} into {branch}")
    repo.git.merge(original_branch)
    print(f"push {branch}")
    repo.git.push("origin", branch)
    print(f"going back to {original_branch}")
    repo.git.checkout(original_branch)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
