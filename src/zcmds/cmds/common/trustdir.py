# powershell -Command "Add-MpPreference -ExclusionPath 'C:\dev'"


"""
Add a folder to the trusted exclusion list of the os
"""

import argparse
import os
import sys
import warnings


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", help="Directories to trust")
    return parser.parse_args()


def _trust_win32(folders: list[str]) -> None:
    for folder in folders:
        cmd = f"powershell -Command \"Add-MpPreference -ExclusionPath '{folder}'\""
        os.system(cmd)


def _trust_linux(folders: list[str]) -> None:
    for folder in folders:
        cmd = f'echo "{folder}" >> /etc/clamav/clamd.conf'
        os.system(cmd)


def _trust_darwin(folders: list[str]) -> None:
    for folder in folders:
        cmd = f'echo "{folder}" >> /etc/clamav/clamd.conf'
        os.system(cmd)


def main() -> int:
    args = parse_arguments()
    dirs = args.directories
    if sys.platform == "win32":
        _trust_win32(dirs)
        return 0
    elif sys.platform == "linux":
        _trust_linux(dirs)
        return 0
    elif sys.platform == "darwin":
        _trust_darwin(dirs)
        return 0
    else:
        warnings.warn(f"Platform {sys.platform} not supported")
        return 1


if __name__ == "__main__":
    sys.exit(main())
