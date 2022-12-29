"""
Finds a file with the given glob file name.
"""

import argparse
import glob
import os


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="glob file name", nargs="?")
    parser.add_argument("--cwd", help="current working directory", default=os.getcwd())
    args = parser.parse_args()

    file: str = os.path.expanduser(args.file) if args.file else input("File: ")
    # trim file
    args.file = file.strip()
    found = False
    for root, _, files in os.walk(os.getcwd()):
        for name in files:
            if glob.fnmatch.fnmatch(name, file):  # type: ignore
                print(os.path.join(root, name))
                found = True
    if not found:
        print("File not found")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
