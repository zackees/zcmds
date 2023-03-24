"""
This module contains a function which_all which returns all the paths where
the program name could be found. This is useful if you want to know if there
are multiple versions of a program on the system.
"""

import os
import sys


def which_all(progname: str, filter_package_exes=False) -> list:
    """Returns all the paths where the program name could be found."""
    # filter_package_exes filters out paths that are in the python directory.
    if os.name == "nt":
        paths = _which_all_win32(progname)
    else:
        paths = _which_all_unix(progname)
        # Remove adjacent duplicates
    out = []
    for i, elem in enumerate(paths):
        if i < len(paths) - 1:
            if elem != paths[i + 1]:
                out.append(elem)
        else:
            out.append(elem)
    if filter_package_exes:
        out = [x for x in out if not _is_in_python_dir(x)]
    return out


def _is_in_python_dir(path: str) -> bool:  # pylint: disable=too-many-return-statements
    """Returns True if the path is in the python directory."""
    dirname = os.path.dirname(path)
    if sys.platform == "win32":
        if os.path.exists(os.path.join(dirname, "python.exe")):
            return True
        if os.path.exists(os.path.join(dirname, "pythonw.exe")):
            return True
        if os.path.exists(os.path.join(dirname, "python3.exe")):
            return True
        if os.path.exists(os.path.join(dirname, "python3w.exe")):
            return True
        # batch file
        if os.path.exists(os.path.join(dirname, "python.bat")):
            return True
        if os.path.exists(os.path.join(dirname, "python3.bat")):
            return True
    else:
        if os.path.exists(os.path.join(dirname, "python")):
            return True
        if os.path.exists(os.path.join(dirname, "python3")):
            return True
    return False


def _which_all_win32(progname: str) -> list:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    found_executables = []
    pname, ext = os.path.splitext(progname)
    extra_paths = [".exe", ".bat", ".cmd"]
    if ext:
        # We are doing an exact match, so don't add any extensions
        for path in paths:
            full_path = os.path.join(path, progname)
            if os.path.exists(full_path):
                found_executables.append(full_path)
    else:
        # We are doing a partial match, so add extensions
        for path in paths:
            for ext in extra_paths:
                full_path = os.path.join(path, pname + ext)
                if os.path.exists(full_path):
                    found_executables.append(full_path)
    # Remove adjacent duplicates
    return found_executables


def _which_all_unix(progname: str) -> list:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    found_executables = []
    # We are doing an exact match, so don't add any extensions
    for path in paths:
        full_path = os.path.join(path, progname)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            found_executables.append(full_path)
    return found_executables


def main() -> None:
    """Prints the paths where the program name could be found."""
    if len(sys.argv) < 2:
        print("Usage: whichall <progname>")
        sys.exit(1)
    progname = sys.argv[1]
    paths = which_all(progname)
    for path in paths:
        print(path)
    sys.exit(0)
