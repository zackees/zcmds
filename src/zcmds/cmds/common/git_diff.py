import argparse
import shutil
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from git import Repo


class DiffTool(ABC):
    @abstractmethod
    def diff(self, path1: Path, path2: Path):
        pass


class DiffToolWindows(DiffTool):
    def __init__(self, tool: Path) -> None:
        assert tool.exists(), f"Tool {tool} does not exist."
        self.tool = tool

    def diff(self, path1: Path, path2: Path) -> int:
        cmd = f'"{self.tool}" "{path1}" "{path2}"'
        print(f"Running command: {cmd}")
        result = subprocess.run([str(self.tool), str(path1), str(path2)], check=False)
        rtn = result.returncode
        return rtn


def get_diff_tool() -> DiffTool:
    if sys.platform == "win32":
        path = Path(r"C:\Program Files\Beyond Compare 5\BCompare.exe")
        assert path.exists(), f"Beyond Compare not found at {path}."
        return DiffToolWindows(path)
    raise NotImplementedError("Only Windows is supported.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diff a file in git",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file", type=Path, help="The file to diff.", nargs="?")
    args = parser.parse_args()
    return args


def branch_exists(repo: Repo, branch: str) -> bool:
    """Returns True if the branch exists."""
    return branch in [b.name for b in list(repo.branches())]


def run(args: argparse.Namespace) -> int:
    try:
        # Get the file in the current branch
        file = args.file
        if not file:
            file = Path(input("Enter the file to diff: ").strip())
        repo = Repo(".")
        answer = input("Diff against the current branch? [Y/n] ").strip()
        if answer.lower() != "y":
            branch = input("Enter the branch to diff against: ").strip()
            assert branch_exists(repo, branch), f"Branch {branch} does not exist."
        else:
            branch = None
        diff_tool = get_diff_tool()
        # Get the current branch
        current_branch = repo.active_branch

        temp_dir = tempfile.mkdtemp()
        temp_file = Path(temp_dir) / file.name

        if branch:
            # Copy the file from the specified branch to the temporary directory
            repo.git.checkout(branch)
            shutil.copy(file, temp_file)
            repo.git.checkout(current_branch)
        else:
            # If no branch is specified, just copy the current file to the temporary directory
            shutil.copy(file, temp_file)

        # Perform the diff
        result = diff_tool.diff(file, temp_file)
        if result != 0:
            print(f"Diff tool returned non-zero exit code: {result}")
            return result
    finally:
        shutil.rmtree(temp_dir)

    print("Diff completed successfully.")

    return 0


def main() -> int:
    try:
        args = parse_args()
        return run(args)
    except KeyboardInterrupt:
        print("Exiting...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
