# pylint: skip-file

import argparse
import os
import sys


def main():
    # Expects a single argument: the path to the video file to shrink
    parser = argparse.ArgumentParser(description="Shrink a video file")
    parser.add_argument("video_path", help="Path to the video file to shrink")
    # Adds optional crf argument
    parser.add_argument("--crf", help="CRF value to use", type=int, default=26)
    # Adds optional height argument
    parser.add_argument(
        "--height", help="height of the output video, e.g 1080 = 1080p", default=480
    )
    parser.add_argument(
        "--downmix", help="downmix the audio from stereo to mono", action="store_true"
    )
    parser.add_argument(
        "--fps",
        help="frames per second of the output video, default is no framerate change",
        default=None,
    )
    args = parser.parse_args()
    filename = args.video_path
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    height = args.height
    crf = args.crf
    path, _ = os.path.splitext(filename)
    out_path = f"{path}_small.mp4"

    downmix_stmt = "-ac 1" if args.downmix else ""
    fps_stmt = f"fps=fps={args.fps}," if args.fps else ""
    filter_stmt = f'-vf "{fps_stmt}scale=trunc(oh*a/2)*2:{height}"'
    # trunc(oh*...) fixes issue with libx264 encoder not liking an add number of width pixels.
    cmd = f'static_ffmpeg -hide_banner -y -i "{filename}" {filter_stmt} {downmix_stmt} -movflags +faststart -preset veryslow -c:v libx264 -crf {crf} "{out_path}"'
    print(f"Running:\n  {cmd}")
    os.system(cmd)


if __name__ == "__main__":
    main()
