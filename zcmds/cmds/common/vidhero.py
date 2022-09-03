import argparse
import os
import sys


def timecode_to_seconds(timecode):
    """
    Converts a timecode to seconds
    """
    time_parts = [t for t in timecode.split(":") if t]
    time_parts = time_parts[::-1]
    seconds = int(time_parts[0])
    if len(time_parts) > 1:
        seconds += int(time_parts[1]) * 60
    if len(time_parts) > 2:
        seconds += int(time_parts[2]) * 60 * 60
    return seconds


def main():
    # Expects a single argument: the path to the video file to shrink
    parser = argparse.ArgumentParser(
        description="Make a looping video with a fade in and out"
    )
    parser.add_argument("video_path", help="Path to the video input file")
    # Adds optional crf argument
    parser.add_argument("--crf", help="CRF value to use", type=int, default=28)
    # Adds optional height argument
    parser.add_argument(
        "--start_timecode", help="start timecode like 0:38", required=True
    )
    parser.add_argument("--end_timecode", help="end timecode like 0:48", required=True)
    parser.add_argument("--height", help="output path", required=True)
    args = parser.parse_args()
    video_path = args.video_path or input("Enter video path: ")
    start_timecode = args.start_timecode or input("Enter start timecode like 0:38: ")
    end_timecode = args.end_timecode or input("Enter end timecode like 0:48: ")

    if not os.path.exists(video_path):
        print(f"{video_path} does not exist")
        sys.exit(1)
    height = args.height
    crf = args.crf
    path, _ = os.path.splitext(video_path)
    out_path = os.path.join(path, f"{os.path.basename(path)}_hero_{height}.mp4")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # trunc(oh*...) fixes issue with libx264 encoder not liking an add number of width pixels.
    start_seconds = timecode_to_seconds(start_timecode)
    end_seconds = timecode_to_seconds(end_timecode)
    cmd = f'static_ffmpeg -hide_banner -i "{video_path}" -ss {start_timecode} -to {end_timecode} -vf "scale=trunc(oh*a/2)*2:{height},fade=t=in:st={start_seconds}:d=1,fade=t=out:st={end_seconds-1}:d=1" -movflags +faststart -preset veryslow -c:v libx264 -crf {crf} "{out_path}"'
    print(f"Running:\n\n  {cmd}\n")
    os.system(cmd)
    print("Generted file: " + out_path)


if __name__ == "__main__":
    main()
