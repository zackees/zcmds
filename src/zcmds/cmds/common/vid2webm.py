# pylint: skip-file

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

VERSION = "0.1.0"


def main():
    parser = argparse.ArgumentParser(description="Convert video to mp4")
    parser.add_argument("filename", help="Path to video file", nargs="?")
    parser.add_argument("--rencode", help="rencode the video", action="store_true")
    parser.add_argument("--version", help="Print version and exit", action="store_true")
    parser.add_argument("--crf", help="CRF value", default=None, type=Optional[int])
    args = parser.parse_args()
    filename = args.filename or input("filname: ")
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    out_path = Path(filename).with_suffix(".webm")
    crf = args.crf or int(input("crf: "))
    cmd = f'static_ffmpeg -hide_banner -i "{filename}" -preset veryslow -vcodec libvpx -acodec libvorbis -crf {crf} "{out_path}"'
    os.system(cmd)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
