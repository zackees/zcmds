"""
Runs the lint command in the current directory.
"""

import argparse
import os
import subprocess
import sys

from zcmds.util.find_bash import find_bash


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("args", nargs="*", help="Arguments to pass to the lint command")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    # Check if a lint file exists in the current directory
    test_file = os.path.join(os.getcwd(), "test")
    if not os.path.exists(test_file):
        print("No test file found in the current directory.")
        return 1
    # Run the lint file with bash
    bash_exe = find_bash()
    # cmd = ["bash", lint_file] + args.args
    cmd = [str(bash_exe), test_file] + args.args
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
