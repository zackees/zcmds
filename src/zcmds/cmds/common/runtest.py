"""
Runs the test command in the current directory or parent directories.
"""

import argparse
import os
import subprocess
import sys

from zcmds.util.find_bash import find_bash
from zcmds.util.find_file_in_parents import find_file_in_parents


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("args", nargs="*", help="Arguments to pass to the test command")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    start_dir = os.getcwd()

    # Find the test file
    test_file, level = find_file_in_parents(start_dir, "test")

    if not test_file:
        print("No test file found in the current directory or parent directories.")
        return 1

    # If test file is more than 3 levels up, prompt the user
    if level > 3:
        print(f"Test file found {level} levels up at: {test_file}")
        response = input("Do you want to run it? (y/n): ").strip().lower()
        if response != "y":
            print("Test operation cancelled.")
            return 0

    # Change to the directory containing the test file
    test_dir = os.path.dirname(test_file)
    if test_dir != start_dir:
        os.chdir(test_dir)
        print(f"Changed directory to: {test_dir}")

    # Run the test file with bash
    bash_exe = find_bash()
    cmd = [str(bash_exe), test_file] + args.args
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
