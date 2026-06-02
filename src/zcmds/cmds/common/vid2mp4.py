# pylint: skip-file

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


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


def build_ffmpeg_command(
    filename: str,
    out_path: Path,
    *,
    rencode: bool,
    codec: str,
    preset: str,
    crf: int,
    height: int | None,
) -> list[str]:
    if not rencode:
        return ["ffmpeg", "-i", filename, "-c", "copy", str(out_path)]

    command = ["static_ffmpeg", "-hide_banner", "-i", filename]
    if height:
        command.extend(["-vf", f"scale=trunc(oh*a/2)*2:{height}"])

    command.extend(["-vcodec", codec, "-preset", preset])
    if codec == "h264_nvenc":
        command.extend(["-rc", "constqp", "-qp", str(crf or 23)])
    else:
        command.extend(["-crf", str(crf or 23)])

    command.extend(["-c:a", "copy", "-y", str(out_path)])
    return command


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert video to mp4")
    parser.add_argument("filename", help="Path to video file", nargs="?")
    parser.add_argument("--rencode", help="Rencode the video", action="store_true")
    parser.add_argument("--nvenc", help="Use NVENC encoder", action="store_true")
    parser.add_argument(
        "--preset",
        help="Preset for the output video",
        default=None,
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
    args = parser.parse_args(argv)
    if args.version:
        print(VERSION)
        return 0
    if not args.filename:
        parser.error("filename is required")
    should_rencode = bool(args.rencode or args.nvenc or args.crf or args.height)
    filename = args.filename
    if not os.path.exists(filename):
        print(f"{filename} does not exist", file=sys.stderr)
        return 1
    out_path = Path(filename).with_suffix(".mp4")
    if out_path.exists():
        # Remove suffix from file name and add _converted.mp4
        out_path = (
            Path(filename)
            .with_suffix("")
            .with_name(f"{Path(filename).stem}_converted.mp4")
        )

    codec = "h264_nvenc" if args.nvenc else "libx264"

    # Set preset based on encoder if not explicitly provided
    if args.preset:
        preset = args.preset
        # Validate preset matches encoder
        if args.nvenc and preset in X264_PRESETS and preset not in NVENC_PRESETS:
            print(
                f"Error: Preset '{preset}' is not valid for NVENC encoder.",
                file=sys.stderr,
            )
            print(f"Valid NVENC presets: {', '.join(NVENC_PRESETS)}", file=sys.stderr)
            return 1
        elif not args.nvenc and preset in NVENC_PRESETS and preset not in X264_PRESETS:
            print(
                f"Warning: Preset '{preset}' is NVENC-specific. Using with x264.",
                file=sys.stderr,
            )
    elif args.nvenc:
        preset = "slow"  # Default NVENC preset
    else:
        preset = "veryslow"  # Default x264 preset

    cmd = build_ffmpeg_command(
        filename,
        out_path,
        rencode=should_rencode,
        codec=codec,
        preset=preset,
        crf=args.crf,
        height=args.height,
    )
    print(f"Running:\n  {subprocess.list2cmdline(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"ffmpeg failed with exit code {result.returncode}", file=sys.stderr)
        return result.returncode
    print(f"Generated {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
