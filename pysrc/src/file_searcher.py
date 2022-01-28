#! /usr/bin/python

import fileutils
import os
import sys

sys.path.append('.')


def main():
    args = fileutils.GetSearchArgs()
    for file in fileutils.IterMatchingFiles(cur_dir=args.cur_dir,
                                            file_pattern=args.file_pattern,
                                            text_search_string=args.search_string):
        with open(file) as fd:
            file_data = fd.read()
        matches = []
        for i, line in enumerate(file_data.splitlines()):
            if args.search_string in line:
                matches.append((i, line))

        print("Found %d matches in %s:\n" %
              (len(matches), os.path.abspath(file)))

        for match in matches:
            haystack = match[1].strip()
            #pos = haystack.find(match)
            # if len(haystack) > 60:
            #  haystack = haystack[0:60] + '...'
            print("  %s: %s" % (match[0], haystack))


if __name__ == "__main__":
    main()
