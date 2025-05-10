"""
Runs the lint command in the current directory or parent directories.
"""

import argparse
import os
import subprocess
import sys

from zcmds.util.find_bash import find_bash
from zcmds.util.find_file_in_parents import find_file_in_parents


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("args", nargs="*", help="Arguments to pass to the lint command")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    start_dir = os.getcwd()

    # Find the lint file
    lint_file, level = find_file_in_parents(start_dir, "lint")

    if not lint_file:
        print("No lint file found in the current directory or parent directories.")
        return 1

    # If lint file is more than 3 levels up, prompt the user
    if level > 3:
        print(f"Lint file found {level} levels up at: {lint_file}")
        response = input("Do you want to run it? (y/n): ").strip().lower()
        if response != "y":
            print("Lint operation cancelled.")
            return 0

    # Change to the directory containing the lint file
    lint_dir = os.path.dirname(lint_file)
    if lint_dir != start_dir:
        os.chdir(lint_dir)
        print(f"Changed directory to: {lint_dir}")

    # Run the lint file with bash
    bash_exe = find_bash()
    cmd = [str(bash_exe), lint_file] + args.args
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
