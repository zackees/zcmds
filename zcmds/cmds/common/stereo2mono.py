# pylint: skip-file

import os
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print(f"Expected two args, but got {len(sys.argv)} instead.")
        sys.exit(1)
    filename = sys.argv[1:2][0]
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    out_left_path = Path("left_" + filename).with_suffix(".wav")
    out_right_path = Path("right_" + filename).with_suffix(".wav")
    cmd0 = f'ffmpeg -i %1 -filter_complex "[0:a]channelsplit=channel_layout=stereo:channels=FR[right]" -map "[right]" {out_right_path}'
    cmd1 = f'ffmpeg -i %1 -filter_complex "[0:a]channelsplit=channel_layout=stereo:channels=FL[left]" -map "[left]" {out_left_path}'
    os.system(cmd0)
    os.system(cmd1)


if __name__ == "__main__":
    main()
