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


def get_audio_channels(vidfile: str) -> int:
    """Returns the number of channels of the given video file."""
    cmd = (
        "static_ffprobe -v error -select_streams a:0 -show_entries stream=channels"
        f' -of default=nokey=1:noprint_wrappers=1 "{vidfile}"'
    )
    return int(subprocess.check_output(cmd, shell=True, universal_newlines=True).strip())


def get_video_bitrate(vidfile: str) -> int:
    """Returns the bitrate of the given video file."""
    cmd = (
        "static_ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate"
        f' -of default=nokey=1:noprint_wrappers=1 "{vidfile}"'
    )
    return int(subprocess.check_output(cmd, shell=True, universal_newlines=True).strip())


def format_duration(duration: float) -> str:
    """Returns a string representation of the given duration."""
    hours = int(duration / 3600)
    duration -= hours * 3600
    minutes = int(duration / 60)
    duration -= minutes * 60
    seconds = int(duration)
    duration -= seconds
    milliseconds = int(duration * 1000)
    out = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    while out.startswith("00:"):
        out = out[3:]
    return out


def get_format_json(vidfile: str) -> str:
    """Returns the format json of the given video file."""
    cmd = f'static_ffprobe -v error -print_format json -show_format -show_streams "{vidfile}"'
    return subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()


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
        try:
            video_encoder = get_video_encoder(infile)
            video_height = get_video_height(infile)
            video_width = get_video_width(infile)
            video_duration = get_video_duration(infile)
            video_duration_str = format_duration(video_duration)
            video_bitrate = get_video_bitrate(infile)
            video_bitrate_str = f"{video_bitrate / 1000000:.2f} Mbps"
            print("Video:")
            print(f"  Encoder: {video_encoder}")
            print(f"  Height: {video_height}")
            print(f"  Width: {video_width}")
            print(f"  Duration: {video_duration_str}")
            print(f"  Bitrate: {video_bitrate_str}")
        except subprocess.CalledProcessError:
            print("No video stream found")

        try:
            audio_encoder = get_audio_encoder(infile)
            if not audio_encoder:
                print("No audio stream found")
            else:
                audio_bitrate = get_audio_bitrate(infile)
                audio_bitrate_str = f"{audio_bitrate / 1000:.0f} kbps"
                audio_channels = get_audio_channels(infile)
                print("Audio:")
                print(f"  Encoder: {audio_encoder}")
                print(f"  Bitrate: {audio_bitrate_str}")
                print(f"  Channels: {audio_channels}")
        except subprocess.CalledProcessError:
            print("No audio stream found")
    else:
        json_str = get_format_json(infile)
        print(json_str)


if __name__ == "__main__":
    main()
