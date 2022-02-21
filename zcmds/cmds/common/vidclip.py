# pylint: skip-file

import os
import sys
import argparse


def sanitize(s: str) -> str:
    return s.replace(":", "-")


def stripext(s: str) -> str:
    return os.path.splitext(s)[0]


def main():

    parser = argparse.ArgumentParser(
        description="Cuts clips from local files.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input")
    parser.add_argument("--start_timestamp", help="start of the clip")
    parser.add_argument("--length", help="length of the clip")
    parser.add_argument("--outname", help="output name of the file")
    parser.add_argument(
        "--crf", default="18", type=int, help="crf quality of the file."
    )
    args = parser.parse_args()

    infile = args.input
    start_timestamp = args.start_timestamp or input("start_timestamp: ")
    length = args.length or input("length (seconds): ")
    output_path = args.outname or stripext(infile) + "_clip.mp4"
    crf = args.crf  # The amount of quality, 0 is lossless and 50 is shit.

    print(infile)
    if not os.path.exists(infile):
        print(f"{infile} does not exist")
        sys.exit(1)
    cmd = f'ffmpeg -i "{infile}" -c:v libx264 -crf {crf} -ss {start_timestamp} -t {length} "{output_path}"'
    os.system(cmd)
    if not os.path.exists(output_path):
        print(f"Error, did not generate {output_path}")
    else:
        print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
