import datetime
import os
import subprocess


def duration_to_timestamp(duration):
    # duration is in seconds float, convert to timestamp
    timestamp = datetime.timedelta(seconds=duration)
    return timestamp


def print_file(file):
    stdout = "ERROR"
    try:
        stdout = subprocess.check_output(
            f'static_ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file}"',
            shell=True,
            universal_newlines=True,
        ).strip()
        # convert to float
        duration = duration_to_timestamp(float(stdout))
        print(f"{file}: {duration}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {file}: {e.output}")


def main():
    # Walk the current directory and find all the video files with *.mp4 or *.webm
    vidfiles = []
    for root, dirs, files in os.walk("."):
        for file in files:
            # get the extension of the file
            ext = os.path.splitext(file)[1]
            if ext in [".mp4", ".webm", ".mkv", ".avi", ".mov"]:
                file_path = os.path.join(root, file)
                vidfiles.append(file_path)

    for vid in vidfiles:
        print_file(vid)


if __name__ == "__main__":
    main()
