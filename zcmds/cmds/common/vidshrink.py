# pylint: skip-file

import argparse
import os
import sys


def main():

    # Expects a single argument: the path to the video file to shrink
    parser = argparse.ArgumentParser(description="Shrink a video file")
    parser.add_argument("video_path", help="Path to the video file to shrink")
    # Adds optional crf argument
    parser.add_argument("--crf", help="CRF value to use", type=int, default=19)
    # Adds optional height argument
    parser.add_argument("--height", help="height of the output video, e.g 1080 = 1080p", default=480)
    args = parser.parse_args()
    filename = args.video_path
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    height = args.height
    crf = args.crf
    path, _ = os.path.splitext(filename)
    out_path = f"{path}_small.mp4"
    cmd = f'static_ffmpeg -hide_banner -i "{filename}" -vf scale=-1:{height} -c:v libx264 -crf {crf} "{out_path}"'
    os.system(cmd)


if __name__ == "__main__":
    main()
