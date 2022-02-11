import os
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print(f"Expected one arg, but got {len(sys.argv)} instead.")
        sys.exit(1)
    chop_seconds = int(input("how many seconds? "))
    filename = sys.argv[1:2][0]
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    out_path = Path(filename).with_stem(f"chopped_{filename}").with_suffix(".mp4")
    cmd = f'ffmpeg -i "{filename}" -ss {chop_seconds} -c copy "{out_path}"'
    os.system(cmd)


if __name__ == "__main__":
    main()
