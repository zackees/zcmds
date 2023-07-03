# pylint: skip-file

import argparse
import os
import sys
from pathlib import Path

VERSION = "0.2.0"

X264_PRESETS = [
    "veryslow",
    "slow",
    "medium",
    "fast",
    "faster",
    "veryfast",
    "superfast",
    "ultrafast",
]
NVENC_PRESETS = [
    "default",
    "slow",
    "medium",
    "fast",
    "high-quality",
    "high-performance",
    "low-latency",
    "low-latency-high-quality",
    "low-latency-high-performance",
]
ALL_PRESETS = X264_PRESETS + NVENC_PRESETS


def main():
    parser = argparse.ArgumentParser(description="Convert video to mp4")
    parser.add_argument("filename", help="Path to video file", nargs="?")
    parser.add_argument("--rencode", help="Rencode the video", action="store_true")
    parser.add_argument("--nvenc", help="Use NVENC encoder", action="store_true")
    parser.add_argument(
        "--preset",
        help="Preset for the output video",
        default="veryslow",
        choices=ALL_PRESETS,
    )
    parser.add_argument(
        "--crf",
        help="CRF value for the output video (0-51). Lower values mean better quality.",
        type=int,
        default=23,
    )
    parser.add_argument("--height", help="Output video height.", type=int, default=None)
    parser.add_argument("--version", help="Print version and exit", action="store_true")
    args = parser.parse_args()
    if args.version:
        print(VERSION)
        sys.exit(0)
    args.rencode = args.rencode or args.nvenc or args.crf or args.height
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

    codec = "h264_nvenc" if args.nvenc else "libx264"
    preset = args.preset or "hq" if args.nvenc else "veryslow"
    scale_cmd = f'-vf scale="trunc(oh*a/2)*2:{args.height}"' if args.height else ""

    if args.rencode:
        quality_stmt = f"-crf {args.crf}" if args.crf else "-b:v 0 -crf 23"
        if codec == "h264_nvenc":
            quality_stmt = f"-cq {args.crf}" if args.crf else "-cq 23"
        cmd = f'static_ffmpeg -hide_banner -i "{filename}" {scale_cmd} -vcodec {codec} -preset {preset} {quality_stmt} -c:a copy -y "{out_path}"'
    else:
        cmd = f'ffmpeg -i "{filename}" -c copy "{out_path}"'
    print(f"Running:\n  {cmd}")
    os.system(cmd)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
