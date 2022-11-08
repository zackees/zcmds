# pylint: skip-file

import argparse
import os
import subprocess
import sys
from typing import Tuple


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


def get_video_encoder(vidfile: str) -> str:
    """Returns the encoder used for the given video file."""
    cmd = (
        "static_ffprobe -v error -select_streams v:0 -show_entries stream=codec_name"
        f' -of default=nokey=1:noprint_wrappers=1 "{vidfile}"'
    )
    return subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()


def get_audio_encoder(vidfile: str) -> str:
    """Returns the encoder used for the given video file."""
    cmd = (
        "static_ffprobe -v error -select_streams a:0 -show_entries stream=codec_name"
        f' -of default=nokey=1:noprint_wrappers=1 "{vidfile}"'
    )
    return subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()


def get_video_height(vidfile: str) -> int:
    """Returns the height of the given video file."""
    cmd = (
        "static_ffprobe -v error -select_streams v:0 -show_entries stream=height"
        f' -of default=nokey=1:noprint_wrappers=1 "{vidfile}"'
    )
    return int(subprocess.check_output(cmd, shell=True, universal_newlines=True).strip())


def get_video_width(vidfile: str) -> int:
    """Returns the width of the given video file."""
    cmd = (
        "static_ffprobe -v error -select_streams v:0 -show_entries stream=width"
        f' -of default=nokey=1:noprint_wrappers=1 "{vidfile}"'
    )
    return int(subprocess.check_output(cmd, shell=True, universal_newlines=True).strip())


def get_video_duration(vidfile: str) -> float:
    """Returns the duration of the given video file."""
    cmd = (
        "static_ffprobe -v error -select_streams v:0 -show_entries stream=duration"
        f' -of default=nokey=1:noprint_wrappers=1 "{vidfile}"'
    )
    return float(subprocess.check_output(cmd, shell=True, universal_newlines=True).strip())


def get_audio_bitrate(vidfile: str) -> int:
    """Returns the bitrate of the given video file."""
    cmd = (
        "static_ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate"
        f' -of default=nokey=1:noprint_wrappers=1 "{vidfile}"'
    )
    return int(subprocess.check_output(cmd, shell=True, universal_newlines=True).strip())


def main():
    parser = argparse.ArgumentParser(
        description="Cuts clips from local files.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input", nargs="?")
    parser.add_argument("--full", help="full ffprobe output", action="store_true")
    args = parser.parse_args()
    infile = args.input or input("Input video: ")
    if not infile:
        print("No input file specified")
        sys.exit(1)
    if not os.path.exists(infile):
        print(f"File '{infile}' does not exist")
        sys.exit(1)
    if not args.full:
        video_encoder = get_video_encoder(infile)
        video_height = get_video_height(infile)
        video_width = get_video_width(infile)
        video_duration = get_video_duration(infile)
        audio_encoder = get_audio_encoder(infile)
        audio_bitrate = get_audio_bitrate(infile)
        print("Video:")
        print(f"  Encoder: {video_encoder}")
        print(f"  Height: {video_height}")
        print(f"  Width: {video_width}")
        print(f"  Duration: {video_duration}")
        print("Audio:")
        print(f"  Encoder: {audio_encoder}")
        print(f"  Bitrate: {audio_bitrate}")

    else:
        cmd = f'static_ffprobe -v error -show_format -show_streams "{infile}"'
        rtn, stdout, stderr = exec(cmd)
        if rtn != 0:
            print(f"Error: {stderr}")
            sys.exit(1)
        print(stdout)


if __name__ == "__main__":
    main()
