#! /usr/bin/python

import argparse
import fnmatch
import os


def GetSearchArgs(require_replace_args=False):
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


def IterMatchingFiles(cur_dir, file_pattern, text_search_string=None):
    for path, dirs, files in os.walk(cur_dir):
        for f in files:
            if fnmatch.fnmatch(f, file_pattern):
                full_path = os.path.join(path, f)
                if text_search_string is None:
                    yield full_path
                else:
                    with open(full_path) as fd:
                        file_data = fd.read()
                    if text_search_string in file_data:
                        yield full_path


def ReplaceInFile(file_path, search_text, replace_text):
    with open(file_path) as fd:
        file_data = fd.read()
    file_data = file_data.replace(search_text, replace_text)
    with open(file_path, "w") as fd:
        fd.write(file_data)
