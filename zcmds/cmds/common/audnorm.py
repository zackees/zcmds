"""
    Normalizes the audio of a video file.
"""

import argparse
import os
import subprocess


def ffprobe_duration(filename: str) -> float:
    """
    Uses ffprobe to get the duration of a video file.
    """
    cmd = f"static_ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}"
    result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    result = result.replace("\n", "").replace(" ", "")
    return float(result)


def _is_media_file(filename: str) -> bool:
    if not os.path.isfile(filename):
        return False
    ext = os.path.splitext(filename.lower())[1]
    return ext in [".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav"]


def main():
    parser = argparse.ArgumentParser(
        description="Print video durations\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("vidfile", help="Path to vid file", nargs="?")
    parser.add_argument("out", help="Path to vid file", nargs="?")
    args = parser.parse_args()
    path = args.vidfile or input("in vid file: ")
    out = args.out or input("out vid file: ")
    if len(os.path.dirname(out)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    assert _is_media_file(path), f"{path} is not a media file"
    cmd = f'ffmpeg-normalize -f "{path}" -o "{out}" -c:a aac -b:a 192k'
    print(f"Executing:\n  {cmd}")
    os.system(cmd)


if __name__ == "__main__":
    main()
