#! /usr/bin/python

import fileutils
import os
import sys

sys.path.append(".")


def main():
    args = fileutils.GetSearchArgs(require_replace_args=True)
    files = []
    for file in fileutils.IterMatchingFiles(
        cur_dir=args.cur_dir,
        file_pattern=args.file_pattern,
        text_search_string=args.search_string,
    ):
        files.append(file)
        with open(file) as fd:
            file_data = fd.read()
        matches = []
        for i, line in enumerate(file_data.splitlines()):
            if args.search_string in line:
                matches.append((i, line))

        print("Found %d matches in %s:" % (len(matches), os.path.abspath(file)))

        for match in matches:
            haystack = match[1].strip()
            # pos = haystack.find(match)
            # if len(haystack) > 60:
            #  haystack = haystack[0:60] + '...'
            print("  %s: %s" % (match[0], haystack))

    if "y" == input("Apply replace? (y/n): ").lower():
        print("Replacing now... %s" % len(files))
        for file in files:
            print("Replace in file %s " % file)
            fileutils.ReplaceInFile(
                file_path=file,
                search_text=args.search_string,
                replace_text=args.replace_string,
            )


if __name__ == "__main__":
    main()
