# pylint: skip-file

import argparse
import os
import sys
from pathlib import Path

VERSION = "0.1.0"


def main():
    parser = argparse.ArgumentParser(description="Convert video to mp4")
    parser.add_argument("filename", help="Path to video file", nargs="?")
    parser.add_argument("--rencode", help="rencode the video", action="store_true")
    parser.add_argument("--version", help="Print version and exit", action="store_true")
    args = parser.parse_args()
    if args.version:
        print(VERSION)
        sys.exit(0)
    filename = args.filename
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    out_path = Path(filename).with_suffix(".mp4")
    if out_path.exists():
        # Remove suffix from file name and add _converted.mp4
        out_path = (
            Path(filename)
            .with_suffix("")
            .with_name(f"{Path(filename).stem}_converted.mp4")
        )

    # -c:v libx264
    if args.rencode:
        cmd = f'static_ffmpeg -hide_banner -i "{filename}" -preset veryslow -vcodec libx264 -preset -crf 18 -c:a copy -y "{out_path}"'
    else:
        cmd = f'ffmpeg -i "{filename}" -c copy "{out_path}"'
    os.system(cmd)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
