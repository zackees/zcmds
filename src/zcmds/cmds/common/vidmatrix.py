# pylint: skip-file

import argparse
import multiprocessing
import os
from typing import Optional

CRF_START = 18
CRF_END = 40
CRF_STEP = 2

ENCODING_PRESET = "veryslow"

# TODO:
# Add hero filter support:
# static_ffmpeg -y -hide_banner -i input.mp4 -ss 2:04 -to 03:08 -vf "fade=t=in:st=124:d=1,fade=t=out:st=187:d=1" -crf 36 -movflags +faststart -tune film -preset veryslow out.mp4


def get_height(filename):
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=height -of default=noprint_wrappers=1 "{filename}"'
    return int(os.popen(cmd).read())


def generate_filters(height: Optional[int]):
    if height is None:
        return ""
    scale_stmt = f"scale=-1:{height}:flags=lanczos"
    # TODO: add a filter for the fade in and out.
    # Example:
    # static_ffmpeg -y -hide_banner -i input.mp4 -ss 2:04 -to 03:08 \
    #  -vf "fade=t=in:st=124:d=1,fade=t=out:st=187:d=1,scale=-1:1080:flags=lanczos" \
    #  -tune film -preset veryslow -threads 17 -c:v libx264 -crf 36 out.mp4
    filters = [scale_stmt]
    return f' -vf "{",".join(filters)}"'


def main():
    parser = argparse.ArgumentParser(
        "Encodes videos into a matrix of different quality settings."
    )
    parser.add_argument("input", help="input", nargs="?")
    parser.add_argument("--start_timestamp", help="start of the clip", required=True)
    parser.add_argument("--end_timestamp", help="length of the clip", required=True)
    parser.add_argument(
        "--height", help="height of the output video, e.g 1080 = 1080p", default=None
    )
    args = parser.parse_args()
    cpu_count = multiprocessing.cpu_count()
    print(f"Detected {cpu_count} cpus")
    thread_count = cpu_count if cpu_count < 2 else cpu_count + 1
    failed = []
    dirname = os.path.splitext(os.path.basename(args.input))[0]
    os.makedirs(dirname, exist_ok=True)
    ENCODER = "libx264"  # Warning libx265 has poor support still.
    thread_arg = ""
    if ENCODER == "libx264":
        thread_arg = f"-threads {thread_count}"
    for crf in range(CRF_START, CRF_END, CRF_STEP):
        get_height(args.input)
        video_filter_stmt = generate_filters(args.height)
        cmd = f'static_ffmpeg -y -hide_banner -i "{args.input}" -movflags +faststart -tune film -preset {ENCODING_PRESET} {thread_arg} -c:v {ENCODER} {video_filter_stmt} -crf {crf} -ss {args.start_timestamp} -to {args.end_timestamp} "{dirname}/{args.height}p_{crf}.mp4"'
        print(f"Executing:\n  {cmd}")
        if 0 != os.system(cmd):
            print(f"Failed to execute {cmd}")
            failed.append(cmd)
    if failed:
        failure_list = "\n".join(failed)
        print(f"Failed to execute the following commands:\n{failure_list}\n")
        return 1
    return 0


if __name__ == "__main__":
    main()
