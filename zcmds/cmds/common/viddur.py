"""
    Lists the video duration of every video found.
"""

import argparse
import os
import subprocess
import sys


def ffprobe_duration(filename: str) -> float:
    """
    Uses ffprobe to get the duration of a video file.
    """
    cmd = f"static_ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}"
    result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    result = result.replace("\n", "").replace(" ", "")
    return float(result)


def _is_movie(filename: str) -> bool:
    if not os.path.isfile(filename):
        return False
    ext = os.path.splitext(filename.lower())[1]
    return ext in [".mp4", ".mkv", ".avi", ".mov"]


def _get_movie_files(start_dir="."):
    """
    Recursively get all files in a directory
    """
    files = [
        os.path.join(start_dir, f)
        for f in os.listdir(start_dir)
        if _is_movie(os.path.join(start_dir, f))
    ]
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Print video durations\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="Path to list file", nargs="?")
    args = parser.parse_args()
    path = args.path or "."

    if not os.path.exists(path):
        print(f"{path} does not exist")
        sys.exit(1)

    if os.path.isfile(path):
        files = [path]
    else:
        files = _get_movie_files(path)
    if files:
        print("DURATION FILENAME\n-------- --------")
        for f in files:
            try:
                duration = ffprobe_duration(f)
                print(f"{duration} {os.path.abspath(f)}")
            except subprocess.CalledProcessError as cpe:
                print(
                    f"{__file__}: Error while processing {cpe.cmd} because of {cpe}"
                    f"\nSTDOUT\n#################\n{cpe.output}"
                )
                continue


if __name__ == "__main__":
    main()
