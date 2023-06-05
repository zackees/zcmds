"""
Finds a file with the given glob file name.
"""

import argparse
import glob
import os
from datetime import datetime
from typing import Callable, Optional


def parse_size(size):
    units = {"b": 1, "k": 10**3, "m": 10**6, "g": 10**9}
    size = size.lower()
    if size[-1] in units:
        return int(size[:-1]) * units[size[-1]]
    else:
        return int(size)


def main(
    sys_args: Optional[list] = None, _print: Optional[Callable[[str], None]] = None
) -> int:
    _print = _print or print
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("file", help="glob file name", nargs="?")
        parser.add_argument(
            "--cwd", help="current working directory", default=os.getcwd()
        )
        parser.add_argument("--remove", help="remove files", action="store_true")
        parser.add_argument("--start", help="start date YYYY-MM-DD", default=None)
        parser.add_argument("--end", help="end date YYYY-MM-DD", default=None)
        parser.add_argument(
            "--larger-than",
            help="filter files larger than size (b, k, m, g)",
            default=None,
        )
        parser.add_argument(
            "--smaller-than",
            help="filter files smaller than size (b, k, m, g)",
            default=None,
        )
        args = parser.parse_args(sys_args)

        start_date = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
        end_date = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None
        # Add time to the end date
        if end_date:
            end_date = end_date.replace(hour=23, minute=59)
        larger_than = parse_size(args.larger_than) if args.larger_than else None
        smaller_than = parse_size(args.smaller_than) if args.smaller_than else None

        file: str = os.path.expanduser(args.file) if args.file else input("File: ")
        # trim file
        args.file = file.strip()
        found = False
        for root, _, files in os.walk(os.getcwd()):
            for name in files:
                if glob.fnmatch.fnmatch(name, file):  # type: ignore
                    try:
                        file_path = os.path.join(root, name)
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        file_size = os.path.getsize(file_path)
                        if (
                            (start_date and file_time < start_date)
                            or (end_date and file_time > end_date)
                            or (larger_than and file_size <= larger_than)
                            or (smaller_than and file_size >= smaller_than)
                        ):
                            continue
                    except Exception:  # pylint: disable=broad-except
                        continue
                    _print(file_path)
                    found = True
                    if args.remove:
                        os.remove(file_path)
        if not found:
            _print("File not found")
            return 1
        return 0
    except KeyboardInterrupt:
        _print("Aborted")
        return 1


if __name__ == "__main__":
    exit(main())
