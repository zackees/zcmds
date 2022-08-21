# pylint: skip-file

import argparse
import os
import sys


def main():

    # Expects a single argument: the path to the video file to shrink
    parser = argparse.ArgumentParser(description="Shrink a video file")
    parser.add_argument("video_path", help="Path to the video file to shrink")
    # Adds optional crf argument
    parser.add_argument("--crf", help="CRF value to use", type=int, default=28)
    # Adds optional height argument
    parser.add_argument("--heights", help="height of the output video, e.g 1080 = 1080p", type=list[int], default=[480, 720, 1080])
    args = parser.parse_args()
    filename = args.video_path
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    for height in args.heights:
        crf = args.crf
        path, _ = os.path.splitext(filename)
        out_path = os.path.join(path, f"{height}.mp4")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        downmix_stmt = "-ac 1" if height <= 480 else ""
        # trunc(oh*...) fixes issue with libx264 encoder not liking an add number of width pixels.
        cmd = f'static_ffmpeg -hide_banner -i "{filename}" -vf scale=trunc(oh*a/2)*2:{height} {downmix_stmt} -movflags +faststart -preset veryslow -c:v libx264 -crf {crf} "{out_path}"'
        print(f"Running:\n  {cmd}")
        os.system(cmd)
        print("Generted file: " + out_path)


if __name__ == "__main__":
    main()
