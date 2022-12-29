import argparse
import os
import sys
import time


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
    parser.add_argument("--start_timecode", help="start timecode like 0:38")
    parser.add_argument("--end_timecode", help="end timecode like 0:48")
    parser.add_argument("--heights", help="1080,720,480", default="1080,720,480")
    parser.add_argument("--mute", help="mute video", action="store_true")
    args = parser.parse_args()
    if os.path.isdir(args.video_path):
        print(f"{args.video_path} is a directory")
        sys.exit(1)
    if not os.path.exists(args.video_path):
        print(f"{args.video_path} does not exist")
        sys.exit(1)
    video_path = args.video_path or input("Enter video path: ")
    start_timecode = args.start_timecode or input("Enter start timecode like 0:38: ")
    end_timecode = args.end_timecode or input("Enter end timecode like 0:48: ")
    heights = [int(val) for val in args.heights.split(",")]
    # sort so that smallest value / fastest encoded first.
    heights.sort()
    if not os.path.exists(video_path):
        print(f"{video_path} does not exist")
        sys.exit(1)
    for height in heights:
        crf = args.crf
        path, _ = os.path.splitext(video_path)
        out_path = os.path.join(path, f"hero_{height}_crf{crf}.mp4")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # trunc(oh*...) fixes issue with libx264 encoder not liking an add number of width pixels.
        start_seconds = timecode_to_seconds(start_timecode)
        end_seconds = timecode_to_seconds(end_timecode)
        videofilter_stmt = (
            "-vf "
            f'"scale=trunc(oh*a/2)*2:{height},'
            f"fade=t=in:st={start_seconds}:d=1,"
            f'fade=t=out:st={end_seconds-1}:d=1"'
        )
        audiofilter_stmt = (
            f'-af "afade=type=in:start_time={start_seconds}:duration=1,'
            f'afade=type=out:start_time={end_seconds-1}:duration=1"'
        )
        cmd = (
            f'static_ffmpeg -y -hide_banner -v quiet -stats -i "{video_path}"'
            f" -ss {start_timecode} -to {end_timecode}"
            f" {videofilter_stmt} "
            f" {audiofilter_stmt} "
            f' -movflags +faststart -preset veryslow -c:v libx264 -crf {crf} "{out_path}"'
        )
        print(f"\nRUNNING:\n  {cmd}\n")
        print("Writing file: " + out_path)
        start_time = time.time()
        os.system(cmd)
        if args.mute:
            cmd = f'vidmute "{out_path}"'
            print(f"\nRUNNING:\n  {cmd}\n")
            os.system(cmd)
        diff_time = time.time() - start_time
        diff_time_str = str(round(diff_time, 1))
        print(f"Generted file: {out_path} in {diff_time_str} seconds")
    print("\nDone!\n")


if __name__ == "__main__":
    main()
