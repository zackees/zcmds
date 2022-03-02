# pylint: skip-file

import os
import sys


def main():
    if len(sys.argv) != 2:
        print(f"Expected two args, but got {len(sys.argv)} instead.")
        sys.exit(1)
    filename = sys.argv[1:2][0]
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    path, _ = os.path.splitext(filename)
    out_path = f"{path}_small.mp4"
    cmd = f'static_ffmpeg -hide_banner -i "{filename}" -vf scale=640:-1 -c:v libx264 -crf 19 "{out_path}"'
    os.system(cmd)


if __name__ == "__main__":
    main()
