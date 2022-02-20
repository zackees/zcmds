import os
import sys
from pathlib import Path

def sanitize(s: str) -> str:
    return s.replace(":", "-")

def stripext(s: str) -> str:
    return os.path.splitext(s)[0]

def main():
    filename = sys.argv[1:2][0]
    start = input("start_timestamp: ")
    end = input("length (secs): ")
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    suffix = f"_clip_{sanitize(start)}_{sanitize(end)}).mp4"
    out_path = stripext(filename) + suffix
    cmd = f'ffmpeg -i "{filename}" -c:v libx264 -crf 18 -ss {start} -t {end} "{out_path}"'
    os.system(cmd)
    if not os.path.exists(out_path):
        print(f"Error, did not generate {out_path}")
    else:
        print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()
