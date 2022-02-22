# pylint: skip-file
"""
    Module for doing file searching stuff.
"""
import os

from . import fileutils


def main():
    """Main program"""
    args = fileutils.get_search_args()
    for file in fileutils.iter_matching_files(
        cur_dir=args.cur_dir,
        file_pattern=args.file_pattern,
        text_search_string=args.search_string,
    ):
        with open(file, encoding="utf-8") as fd:
            file_data = fd.read()
        matches = []
        for i, line in enumerate(file_data.splitlines()):
            if args.search_string in line:
                matches.append((i, line))
        print(f"Found {len(matches)} matches in {os.path.abspath(file)}:\n")
        for match in matches:
            haystack = match[1].strip()
            print(f"  {match[0]}: {haystack}")


if __name__ == "__main__":
    main()
