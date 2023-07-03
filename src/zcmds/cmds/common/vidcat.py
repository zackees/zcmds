"""
Concatenates two videos together
"""

import argparse
import os
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Tuple

_SAMPLE_RATE = 44100
_CRF_DEFAULT = 18


@dataclass
class Resolution:
    width: int
    height: int


def sanitize(s: str) -> str:
    return s.replace(":", "_")


def stripext(s: str) -> str:
    return os.path.splitext(s)[0]


def exec(cmd: str) -> Tuple[int, str, str]:
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr


def get_resolution(infile: str) -> Resolution:
    cmd = f'static_ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "{infile}"'
    rtn, stdout, _ = exec(cmd)
    if rtn != 0:
        print(f"{__file__}: WARNING: '{cmd}' returned code {rtn}")
    try:
        width, height = stdout.split(",")
    except ValueError:
        print(f"{__file__}: ERROR: could not parse resolution from '{stdout}'")
        import sys

        sys.exit(1)
    return Resolution(int(width), int(height))


def get_highest_resolution(infiles: list[str]) -> Resolution:
    resolutions = [get_resolution(infile) for infile in infiles]
    return max(resolutions, key=lambda resolution: resolution.width)


def concatenate_videos(
    infiles: list[str], outname: str, resolution: Resolution, crf: int
) -> None:
    # Scale and re-encode the input videos
    infiles = [os.path.abspath(infile) for infile in infiles]
    with tempfile.TemporaryDirectory() as tmpdir:
        scaled_videos = []
        for i, infile in enumerate(infiles):
            scaled_video = os.path.join(tmpdir, f"_scaled_video_{i}.mp4")
            cmd = f'static_ffmpeg -i "{infile}" -vf "scale={resolution.width}:{resolution.height}" -c:v libx264 -crf {crf} -c:a aac -b:a 128k -ac 2 -ar {_SAMPLE_RATE} "{scaled_video}"'
            rtn, _, _ = exec(cmd)
            if rtn != 0:
                print(f"{__file__}: WARNING: '{cmd}' returned code {rtn}")
            scaled_videos.append(scaled_video)

        # Create the input file list for concatenation
        with open("input.txt", "w") as f:
            for scaled_video in scaled_videos:
                f.write(f"file '{scaled_video}'\n")
        # Concatenate the videos
        cmd = f'static_ffmpeg -f concat -safe 0 -i input.txt -c copy "{os.path.abspath(outname)}"'

        rtn, _, _ = exec(cmd)
        if rtn != 0:
            print(f"{__file__}: WARNING: '{cmd}' returned code {rtn}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Concatenates videos by encoding them to the same resolution.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input", nargs="+")
    parser.add_argument("--outname", help="output name of the file", required=True)
    parser.add_argument(
        "--crf", default=_CRF_DEFAULT, type=int, help="CRF quality of the file."
    )
    parser.add_argument("--height", help="height of the output video, e.g 1080 = 1080p")
    args = parser.parse_args()
    infiles = args.input
    resolution: Resolution = get_highest_resolution(infiles)
    print(f"Highest resolution: {resolution.width}x{resolution.height}")
    concatenate_videos(infiles, args.outname, resolution, args.crf)
    print(f"Concatenated videos saved as {args.outname}")
    return 0


if __name__ == "__main__":
    main()
