# pylint: skip-file

import argparse
import json
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
    cmd = f'static_ffprobe -v quiet -print_format json -show_format -show_streams "{vidfile}"'
    json_str = subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()
    json_data = json.loads(json_str)
    json_str = json.dumps(json_data, indent=4)
    return json_str


def get_format_per_frame(vidfile: str) -> str:
    """Returns the format per frame of the given video file."""
    cmd = f'static_ffprobe -v quiet -print_format json -show_frames "{vidfile}"'
    json_str = subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()
    json_data = json.loads(json_str)
    json_str = json.dumps(json_data, indent=4)
    return json_str


def get_videostream_info(videstream: dict) -> str:
    """Returns a string representation of the given video stream."""
    lines = []
    lines.append("  Video:")
    lines.append(
        f"    Encoder: {videstream['codec_long_name']}, {videstream['codec_tag_string']}"
    )
    # pix format
    pix_fmt = videstream["pix_fmt"]
    lines.append(f"    Pixel format: {pix_fmt}")
    has_bframes = int(videstream.get("has_b_frames", "0"))
    if has_bframes:
        lines.append(f"    B-Frames: {has_bframes}")
    lines.append(f"    Height: {videstream['height']}")
    lines.append(f"    Width: {videstream['width']}")
    lines.append(f"    Duration: {format_duration(float(videstream['duration']))}")
    video_bitrate = videstream["bit_rate"]
    if video_bitrate.isdigit():
        video_bitrate = int(video_bitrate)
        video_bitrate_str = f"{video_bitrate / 1000000:.2f} Mbps"
    lines.append(f"    Bitrate: {video_bitrate_str}")
    lines.append(f"    Frame count: {videstream['nb_frames']}")
    fr_num = int(videstream["r_frame_rate"].split("/")[0])
    fr_den = int(videstream["r_frame_rate"].split("/")[1])
    framerate = float(fr_num) / float(fr_den)
    lines.append(f"    Framerate: {framerate:.2f} fps")
    return "\n".join(lines)


def get_audiostream_info(audiostream: dict) -> str:
    """Returns a string representation of the given audio stream."""
    lines = []
    lines.append("  Audio:")
    lines.append(
        f"    Encoder: {audiostream['codec_long_name']}, {audiostream['codec_tag_string']}"
    )
    lines.append(f"    Channels: {audiostream['channels']}")
    lines.append(f"    Duration: {format_duration(float(audiostream['duration']))}")
    lines.append(f"    Sample rate: {audiostream['sample_rate']}")
    audio_bitrate = audiostream["bit_rate"]
    if audio_bitrate.isdigit():
        audio_bitrate = int(audio_bitrate)
        audio_bitrate_str = f"{audio_bitrate / 1000:.2f} kbps"
    lines.append(f"    Bitrate: {audio_bitrate_str}")
    return "\n".join(lines)


def print_short_info(vidfile: str) -> None:
    """Prints a short info about the given video file."""
    filesize = os.path.getsize(vidfile)
    filesize_str = f"{filesize / 1000000:.2f} MB"
    print(f"File: {vidfile}")
    print(f"  Size: {filesize_str}")
    vidinfo_data = json.loads(get_format_json(vidfile))
    streams = vidinfo_data.get("streams", [])
    has_video_stream = False
    has_audio_stream = False
    for i, stream in enumerate(streams):
        print(f"Track {i}:")
        if stream["codec_type"] == "video":
            has_video_stream = True
            print(get_videostream_info(stream))
        elif stream["codec_type"] == "audio":
            has_audio_stream = True
            print(get_audiostream_info(stream))
    if not has_video_stream or not has_audio_stream:
        print("")
    if not has_video_stream:
        print("(No video stream found)")
    if not has_audio_stream:
        print("(No audio stream found)")


def main():
    parser = argparse.ArgumentParser(
        description="Cuts clips from local files.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input", nargs="?")
    parser.add_argument("--full", help="full ffprobe output", action="store_true")
    parser.add_argument("--per-frame", help="per frame info", action="store_true")
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
            print_short_info(infile)
        except subprocess.CalledProcessError:
            print("No video stream found")

    if args.full:
        json_str = get_format_json(infile)
        json_data = json.loads(json_str)
        if args.per_frame:
            # Merge frame info
            json_frane_str = get_format_per_frame(infile)
            json_frame_data = json.loads(json_frane_str)
            for key in json_frame_data:
                if key not in json_data:
                    json_data[key] = json_frame_data[key]
        json_str = json.dumps(json_data, indent=4)
        print(json_str)


if __name__ == "__main__":
    main()
