# pylint: skip-file

import argparse
import os
import sys
from pathlib import Path


def run(
    filename: str,
    output: str | None,
    normalize: bool,
    start: str | None,
    end: str | None,
    wave: bool,
) -> int:
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    if output:
        out_path = output
        assert out_path.endswith(".mp3") or (wave and out_path.endswith(".wav"))
    else:
        out_path = str(Path(filename).with_suffix(".wav" if wave else ".mp3"))
    cmd = f'static_ffmpeg -hide_banner -i "{filename}"'
    if start:
        cmd += f" -ss {start}"
    if end:
        cmd += f" -to {end}"
    if wave:
        cmd += f' -vn -acodec pcm_s16le -y ".{out_path}"'
    else:
        cmd += f' -vn -c:a libmp3lame -y ".{out_path}"'
    print(f"Executing:\n  {cmd}")
    os.system(cmd)
    assert os.path.exists(f".{out_path}")
    if not normalize:
        os.rename(f".{out_path}", f"{out_path}")
    else:
        cmd = f'audnorm ".{out_path}" "{out_path}"'
        print(f"Executing:\n  {cmd}")
        rtn = os.system(cmd)
        if rtn != 0:
            print(f"Failed to normalize {out_path}")
            return 1
        os.remove(f".{out_path}")
    os.system(cmd)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="The video file to convert to audio")
    parser.add_argument("-o", "--output", help="The output file name")
    parser.add_argument("-n", "--normalize", action="store_true")
    parser.add_argument("--start", help="Start time for cutting (format: HH:MM:SS)")
    parser.add_argument("--end", help="End time for cutting (format: HH:MM:SS)")
    parser.add_argument(
        "--wave", action="store_true", help="Generate .wav file instead of .mp3"
    )
    args = parser.parse_args()
    filename = sys.argv[1:2][0]
    print(f"Converting {filename} to {'wav' if args.wave else 'mp3'}")
    rtn = run(filename, args.output, args.normalize, args.start, args.end, args.wave)
    return rtn


if __name__ == "__main__":
    main()
