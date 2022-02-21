"""
    Helper function to index a file system
"""

import os
import sys


def file_size(file: str) -> str:
    """Return file size as a string"""
    try:
        val = os.stat(file).st_size
        return f"{val}"
    except PermissionError:
        return "-1"
    except FileNotFoundError:
        return "-1"


def _main():
    try:
        for root, _, files in os.walk("/", topdown=False):
            for name in files:
                file = os.path.abspath(os.path.join(root, name))
                print(f'"{file}", {file_size(file)}')
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    _main()
