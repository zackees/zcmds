# pylint: skip-file

import argparse
import os
import subprocess
import sys


def stripext(s: str) -> str:
    return os.path.splitext(s)[0]


def main():
    parser = argparse.ArgumentParser(
        description="Extracts a video frame.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input")
    parser.add_argument("--timestamp", help="start of the clip")
    parser.add_argument("--length", help="length of the clip")
    parser.add_argument("--outname", help="output name of the file")
    parser.add_argument("--no-open-folder", action="store_true", help="debug")
    args = parser.parse_args()
    infile = args.input
    timestamp = args.timestamp or input("timestamp: ")
    length = args.length or input("length (secs): ")
    do_open_folder = not args.no_open_folder
    if args.outname:
        output_path = os.path.splitext(args.outname)[0]
    else:
        output_path = os.path.splitext(args.input)[0]
    output_path = output_path + "_imgs"
    if not os.path.exists(infile):
        print(f"{infile} does not exist")
        sys.exit(1)

    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    # ffmpeg -i foo.avi -r 1 -s WxH -f image2 foo-%03d.jpeg -ss -frames:v
    file_output_fmt = f'"{output_path}/%03d.jpg"'

    cmd = f'static_ffmpeg -hide_banner -i "{infile}" -ss {timestamp} -t {length} -f image2 {file_output_fmt}'
    print(f"Executing:\n  {cmd}\n")
    subprocess.call(cmd, shell=True, universal_newlines=True, stderr=subprocess.DEVNULL)
    if not os.path.exists(output_path):
        print(f"Error, did not generate {output_path}")
        print(f"Error from cmd:\n  {cmd}\n")
    else:
        print(f"Generated images are in directory: {output_path}")
        if do_open_folder:
            if sys.platform == "win32":
                os.system(f"start explorer {output_path}")


if __name__ == "__main__":
    main()
