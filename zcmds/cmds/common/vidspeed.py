"""
    Normalizes the audio of a video file.
"""

import argparse
import os


def ffmpeg_multiply_speed(inputfile: str, speed: float, outfile: str) -> None:
    """
    Uses ffprobe to get the duration of a video file.
    """
    # cmd = f"static_ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}"
    # cmd = f'ffmpeg -i {inputfile} -vf  "setpts=4*PTS" {outfile}'
    speed = 1 / speed
    atempo = 1 / speed
    cmd = f'static_ffmpeg -y -i {inputfile} -filter_complex "[0:v]setpts={speed}*PTS[v];[0:a]atempo={atempo}[a]" -map "[v]" -map "[a]" {outfile}'
    os.system(cmd)


def _is_media_file(filename: str) -> bool:
    if not os.path.isfile(filename):
        return False
    ext = os.path.splitext(filename.lower())[1]
    return ext in [".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav"]


def main():
    parser = argparse.ArgumentParser(
        description="Prints the video volume or sets it.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("vidfile", help="Path to vid file", nargs="?")
    parser.add_argument("--out", help="Path to vid file")
    parser.add_argument("--speed", help="Speed to multiply against", type=float)
    args = parser.parse_args()
    vidfile = args.vidfile or input("in vid file: ")
    speed = args.speed or float(input("speed: "))
    out = args.out or input("out vid file: ")
    if len(os.path.dirname(vidfile)):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    ffmpeg_multiply_speed(vidfile, speed, out)


if __name__ == "__main__":
    main()
