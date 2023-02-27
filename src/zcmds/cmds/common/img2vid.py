"""
Stitches a bunch of files together to make a video.
"""


# pylint: skip-file

import argparse
import os
import subprocess
import sys


def get_files(path):
    """Returns a list of files in a directory sorted by name."""
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files.sort()
    files = [os.path.join(path, f) for f in files]
    return files


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Concats a bunch of images to get together in an video.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input")
    parser.add_argument("--fps", help="fps of the output video", default=30, type=int)
    args = parser.parse_args()
    infile = args.input
    outfile = os.path.splitext(args.input)[0] + ".mp4"
    if not os.path.exists(infile):
        print(f"{infile} does not exist")
        sys.exit(1)
    files = get_files(infile)
    infiles_stmt = ""
    for f in files:
        infiles_stmt += f' -i "{f}"'
    time_per_frame = 1.0 / args.fps
    concat_file_str = ""
    temp_concat_file = ".concat.txt"
    for f in files:
        f = f.replace("\\", "/")
        concat_file_str += f"file {f}\n"
        concat_file_str += f"duration {time_per_frame}\n"
    with open(temp_concat_file, "w") as f:
        f.write(concat_file_str)
    cmd = f'static_ffmpeg -hide_banner -f concat -i {temp_concat_file} -c:v libx264 -start_number 0 -vf "format=yuv420p" -pix_fmt yuv420p {outfile}'
    print(f"Executing:\n  {cmd}\n")
    subprocess.call(cmd, shell=True, universal_newlines=True)
    os.remove(temp_concat_file)


if __name__ == "__main__":
    main()
