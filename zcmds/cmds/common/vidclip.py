# pylint: skip-file

import argparse
import os
import sys


def sanitize(s: str) -> str:
    return s.replace(":", "-")


def stripext(s: str) -> str:
    return os.path.splitext(s)[0]


def main():

    parser = argparse.ArgumentParser(
        description="Cuts clips from local files.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input", nargs="?")
    parser.add_argument("--start_timestamp", help="start of the clip")
    parser.add_argument("--end_timestamp", help="length of the clip")
    parser.add_argument("--outname", help="output name of the file")
    parser.add_argument("--crf", default="18", type=int, help="crf quality of the file.")
    args = parser.parse_args()

    is_interactive = (
        (args.start_timestamp is None)
        and (args.end_timestamp is None)
        and (args.outname is None)
        and (args.crf is None)
    )

    infile = args.input or input("Input video: ")
    ext = os.path.splitext(infile)[1]
    count = 0

    while True:
        start_timestamp = args.start_timestamp or input("start_timestamp: ")
        end_timestamp = args.end_timestamp or input("end_timestamp: ")
        start_timestamp_str = sanitize(start_timestamp)
        end_timestamp_str = sanitize(end_timestamp)
        outpath_hint = stripext(infile) + f"_clip_{start_timestamp_str}_{end_timestamp_str}{ext}"
        output_path = args.outname or input(f"Output path [{outpath_hint}]: ")
        if output_path == "":
            output_path = outpath_hint
        else:
            # Auto-assume an mp4 extension if none is set.
            _, ext = os.path.splitext(output_path)
            if ext == "":
                output_path = output_path + ".mp4"
        count += 1
        crf = args.crf  # The amount of quality, 0 is lossless and 50 is shit.

        print(infile)
        if not os.path.exists(infile):
            print(f"{infile} does not exist")
            sys.exit(1)
        cmd = f'ffmpeg -i "{infile}" -c:v libx264 -crf {crf} -ss {start_timestamp} -to {end_timestamp} "{output_path}"'
        os.system(cmd)
        if not os.path.exists(output_path):
            print(f"Error, did not generate {output_path}")
        else:
            print(f"Generated: {output_path}")
        if not is_interactive:
            break
        if "y" in input("Continue? (y/n): ").lower():
            break
        args.start_timestamp = None
        args.end_timestamp = None
        args.outname = None
        args.output_path = None


if __name__ == "__main__":
    main()
