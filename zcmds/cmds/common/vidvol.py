"""
    Normalizes the audio of a video file.
"""

import argparse
import os


def _is_media_file(filename: str) -> bool:
    if not os.path.isfile(filename):
        return False
    ext = os.path.splitext(filename.lower())[1]
    return ext in [".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav"]


def ffmpeg_adjust_volume(filename: str, volume: float, out_file: str):
    """
    Adjusts the volume of a video file.
    """
    cmd = f'ffmpeg -i "{filename}" -filter:a "volume={volume}" "{out_file}"'
    print(f"Executing:\n  {cmd}")
    os.system(cmd)


def main():
    parser = argparse.ArgumentParser(
        description="Print video durations\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("vidfile", help="Path to vid file", nargs="?")
    parser.add_argument("out", help="Path to vid file", nargs="?")
    parser.add_argument("--volume", help="Volume to adjust to", type=float)
    args = parser.parse_args()
    vidfile = args.vidfile or input("in vid file: ")
    vol = args.volume or input("volume: ")
    out = args.out or input("out vid file: ")
    if len(os.path.dirname(vidfile)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    assert _is_media_file(vidfile), f"{vidfile} is not a media file"
    ffmpeg_adjust_volume(vidfile, vol, out)


if __name__ == "__main__":
    main()
