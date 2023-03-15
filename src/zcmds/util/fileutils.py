"""
    Helper functions for file based operations.
"""

import argparse
import fnmatch
import os
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class SearchArgs:
    cur_dir: str
    file_patterns: list[str]
    search_string: str
    replace_string: str
    ignore_errors: bool


def get_search_args(require_replace_args=False) -> SearchArgs:
    """Generates an ArgumentParser and returns the args."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--cur_dir", default=os.curdir)
    parser.add_argument("--file_pattern", default=None)
    parser.add_argument("--search_string", default=None)
    parser.add_argument("--replace_string", default=None)
    parser.add_argument("--ignore_errors", action="store_true")
    args = parser.parse_args()
    if args.search_string is None:
        args.search_string = input("search string: ")
    if require_replace_args and args.replace_string is None:
        args.replace_string = input("replace string: ")
    if args.file_pattern is None:
        args.file_pattern = input("file search pattern: ")
    search_args = SearchArgs(
        cur_dir=args.cur_dir,
        file_patterns=args.file_pattern.split(","),
        search_string=args.search_string,
        replace_string=args.replace_string,
        ignore_errors=args.ignore_errors,
    )
    return search_args


def match(file: str, file_patterns: list[str]) -> bool:
    """Returns true if the file matches any of the file patterns."""
    for file_pattern in file_patterns:
        if fnmatch.fnmatch(file, file_pattern):
            return True
    return False


def iter_matching_files(
    cur_dir, file_patterns, text_search_string=None, ignore_errors=False
) -> Any:
    """Generates an iterator for matching files."""
    for path, dirs, files in os.walk(cur_dir):  # pylint: disable=unused-variable
        if ".git" in path.split(os.sep):
            continue
        for f in files:  # pylint: disable=invalid-name
            if match(f, file_patterns):
                full_path = os.path.join(path, f)
                if text_search_string is None:
                    yield full_path
                else:
                    with open(
                        full_path, encoding="utf-8"
                    ) as fd:  # pylint: disable=invalid-name
                        try:
                            file_data = fd.read()
                        except UnicodeDecodeError:
                            if ignore_errors:
                                continue
                            sys.stderr.write(
                                f"  {__file__}: Could not read file: {full_path}\n"
                            )
                            continue
                        except PermissionError:
                            sys.stderr.write(
                                f"  {__file__}: Could not read file: {full_path}\n"
                            )
                            continue

                    if text_search_string in file_data:
                        yield full_path


def replace_in_file(file_path, search_text, replace_text) -> None:
    """Replaces all occurences with replace_text."""
    with open(file_path, encoding="utf-8") as fd:  # pylint: disable=invalid-name
        file_data = fd.read()
    file_data = file_data.replace(search_text, replace_text)
    with open(
        file_path, encoding="utf-8", mode="w"
    ) as fd:  # pylint: disable=invalid-name
        fd.write(file_data)
