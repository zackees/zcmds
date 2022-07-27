"""
    Helper functions for file based operations.
"""

import argparse
import fnmatch
import os


def get_search_args(require_replace_args=False):
    """Generates an ArgumentParser and returns the args."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--cur_dir", default=os.curdir)
    parser.add_argument("--file_pattern", default=None)
    parser.add_argument("--search_string", default=None)
    parser.add_argument("--replace_string", default=None)
    args = parser.parse_args()
    if args.file_pattern is None:
        args.file_pattern = input("file search pattern: ")
    if args.search_string is None:
        args.search_string = input("search string: ")
    if require_replace_args and args.replace_string is None:
        args.replace_string = input("replace string: ")
    return args


def iter_matching_files(cur_dir, file_pattern, text_search_string=None):
    """Generates an iterator for matching files."""
    for path, dirs, files in os.walk(cur_dir):  # pylint: disable=unused-variable
        if ".git" in path.split(os.sep):
            continue
        for f in files:  # pylint: disable=invalid-name
            if fnmatch.fnmatch(f, file_pattern):
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
                            # sys.stderr.write(f"  {__file__}: Could not read file: {full_path}\n")
                            continue
                    if text_search_string in file_data:
                        yield full_path


def replace_in_file(file_path, search_text, replace_text):
    """Replaces all occurences with replace_text."""
    with open(file_path, encoding="utf-8") as fd:  # pylint: disable=invalid-name
        file_data = fd.read()
    file_data = file_data.replace(search_text, replace_text)
    with open(
        file_path, encoding="utf-8", mode="w"
    ) as fd:  # pylint: disable=invalid-name
        fd.write(file_data)
