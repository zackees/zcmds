# pylint: skip-file

import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Extracts a video frame.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input")
    parser.add_argument("--outname", help="output name of the file")
    args = parser.parse_args()
    infile = args.input
    if args.outname:
        output_path = os.path.splitext(args.outname)[0]
    else:
        output_path = os.path.splitext(args.input)[0]
    if not os.path.exists(infile):
        print(f"{infile} does not exist")
        sys.exit(1)

    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    # ffmpeg -i foo.avi -r 1 -s WxH -f image2 foo-%03d.jpeg -ss -frames:v
    file_out = f'"{output_path}.gif"'
    cmd = f'static_ffmpeg -hide_banner -y -i "{infile}" -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 {file_out}'
    print(f"Executing:\n  {cmd}\n")
    subprocess.call(cmd, shell=True, universal_newlines=True)
    if not os.path.exists(output_path):
        print(f"Error, did not generate {output_path}")
        print(f"Error from cmd:\n  {cmd}\n")
    else:
        print(f"\nGenerated gif: {file_out}")


if __name__ == "__main__":
    main()
