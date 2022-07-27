"""
    Module for doing file searching and replacing stuff.
"""

import os

from . import fileutils


def main():
    """Main function for search and replace."""
    args = fileutils.get_search_args(require_replace_args=True)
    files = []
    for file in fileutils.iter_matching_files(
        cur_dir=args.cur_dir,
        file_pattern=args.file_pattern,
        text_search_string=args.search_string,
    ):
        files.append(file)
        with open(
            file, encoding="utf-8"
        ) as fd:  # pylint: disable=invalid-name,duplicate-code
            file_data = fd.read()
        matches = []
        for i, line in enumerate(file_data.splitlines()):
            if args.search_string in line:
                matches.append((i, line))

        print(f"Found {len(matches)} matches in {os.path.abspath(file)}:")

        for match in matches:
            haystack = match[1].strip()
            # pos = haystack.find(match)
            # if len(haystack) > 60:
            #  haystack = haystack[0:60] + '...'
            print(f"  {match[0]}: {haystack}")

    if "y" == input("Apply replace? (y/n): ").lower():
        print(f"Replacing now... {len(files)}")
        for file in files:
            print(f"Replace in file {file} ")
            fileutils.replace_in_file(
                file_path=file,
                search_text=args.search_string,
                replace_text=args.replace_string,
            )


if __name__ == "__main__":
    main()
