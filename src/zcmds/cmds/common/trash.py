"""
Sends something to the trash.
"""

import argparse
import sys

from send2trash import send2trash  # type: ignore


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="Files to send to the trash")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    send2trash(args.files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
