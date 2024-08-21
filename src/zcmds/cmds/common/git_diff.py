import argparse
import os
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory

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
        if rtn == 2:
            rtn = 0
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
    parser.add_argument("--branch", type=str, help="The branch to diff against.")
    args = parser.parse_args()
    return args


def branch_exists(repo: Repo, branch: str) -> bool:
    """Returns True if the branch exists."""
    # branches = list(repo.branches())
    branches = repo.branches
    branches_list = list(branches)  # type: ignore
    branch_names = [b.name for b in branches_list]
    return branch in branch_names


def run(args: argparse.Namespace) -> int:
    prev_dir = Path.cwd()
    try:
        with TemporaryDirectory() as temp_dir:
            # Get the file in the current branch
            file = args.file
            if not file:
                file = Path(input("Enter the file to diff: ").strip())
            repo = Repo(".")
            branch = args.branch
            if not branch:
                answer = input("Diff against the current branch? [Y/n] ").strip()
                if answer.lower() != "y":
                    branch = input("Enter the branch to diff against: ").strip()
                else:
                    branch = repo.active_branch
            assert branch_exists(repo, branch), f"Branch {branch} does not exist."
            diff_tool = get_diff_tool()
            temp_dir = tempfile.mkdtemp()
            temp_file = Path(temp_dir) / file.name

            # Copy the file from the specified branch to the temporary directory
            file_content = repo.git.show(f"{branch}:{file}")
            with open(temp_file, "w") as f:
                f.write(file_content)

            # Perform the diff
            result = diff_tool.diff(temp_file, file)
            if result != 0:
                print(f"Diff tool returned non-zero exit code: {result}")
                return result
    finally:
        os.chdir(str(prev_dir))
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
