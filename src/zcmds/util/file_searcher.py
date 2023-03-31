# pylint: skip-file
"""
    Module for doing file searching stuff.
"""
import os

from . import fileutils


def main() -> None:
    """Main program"""
    args: fileutils.SearchArgs = fileutils.get_search_args()
    for file in fileutils.iter_matching_files(
        cur_dir=args.cur_dir,
        file_patterns=args.file_patterns,
        text_search_string=args.search_string,
        ignore_errors=args.ignore_errors,
    ):
        with open(file, encoding="utf-8") as fd:
            file_data = fd.read()
        matches = []
        for i, line in enumerate(file_data.splitlines()):
            if args.search_string in line:
                matches.append((i, line))
        if len(matches):
            # print(f"Found {len(matches)} matches in {os.path.abspath(file)}:")
            for match in matches:
                haystack = match[1].strip()
                absfile = os.path.abspath(file)
                print(f"{absfile}:{match[0]}:\n  {haystack}")
            print()


if __name__ == "__main__":
    main()
