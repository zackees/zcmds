# pylint: skip-file

import argparse
import os
import sys
from pathlib import Path


def run(filename: str, output: str | None, normalize: bool) -> int:
    if not os.path.exists(filename):
        print(f"{filename} does not exist")
        sys.exit(1)
    if output:
        out_path = output
        assert out_path.endswith(".mp3")
    else:
        out_path = str(Path(filename).with_suffix(".mp3"))
    cmd = f'static_ffmpeg -hide_banner -i "{filename}" -vn -c:a libmp3lame -y ".{out_path}"'
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
    parser.add_argument("filename", help="The video file to convert to mp3")
    parser.add_argument("-o", "--output", help="The output file name")
    parser.add_argument("-n", "--normalize", action="store_true")
    args = parser.parse_args()
    filename = sys.argv[1:2][0]
    print(f"Converting {filename} to mp3")
    rtn = run(filename, args.output, args.normalize)
    return rtn


if __name__ == "__main__":
    main()
