import argparse
import sys
import warnings

from git import Repo

from zcmds.util.say import say


def warn(msg: str) -> None:
    """Prints a warning message."""
    warnings.warn(msg)
    say(msg)


def git_has_uncommitted_changes_or_untracked_files() -> tuple[bool, bool]:
    """Returns True if git has uncommitted changes or untracked files."""
    try:
        from git import Repo  # type: ignore
    except ImportError:
        warnings.warn("GitPython is not installed.")
        return False, False
    repo = Repo(".")
    return repo.is_dirty(), len(repo.untracked_files) > 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pushes to git",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    return parser.parse_args()


def main() -> int:
    is_dirty, has_untracked_files = git_has_uncommitted_changes_or_untracked_files()
    if is_dirty:
        msg = "Push failed: there are uncommitted changes that need to be committed or stashed first."
        warn(msg)
        return 1
    if has_untracked_files:
        msg = "Push failed: there are untracked files that need to be committed or removed first."
        warn(msg)
        return 1
    args = parse_args()  # pylint: disable=unused-variable
    args = args  # Silence warnings
    repo = Repo(".")
    original_branch = repo.active_branch
    # fetch the repo
    repo.git.fetch()
    # can rebase succeed?
    # _todo: check if rebase succeeds
    # check if head has changed
    repo.git.push("origin", original_branch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
