# pylint: skip-file

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple


def sanitize(s: str) -> str:
    return s.replace(":", "_")


def stripext(s: str) -> str:
    return os.path.splitext(s)[0]


_CRF_DEFAULT = 18


def exec(cmd: str) -> Tuple[int, str, str]:
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr


# Tests if a path exists, and if it does then it names it with the next number
def get_next_path(path: str) -> str:
    if not os.path.exists(path):
        return path
    else:
        base, ext = os.path.splitext(path)
        return get_next_path(f"{base}_alt{ext}")


def encode(
    infile, height, crf, start_timestamp, end_timestamp, output_path, print_fcn
) -> bool:
    vf_scale_part = ""
    to_stmt = ""
    from_stmt = ""
    if height:
        vf_scale_part = f"-vf trunc(oh*a/2)*2:{height}"
    
    if start_timestamp:
        from_stmt = f"-ss {start_timestamp}"
    if end_timestamp:
        to_stmt = f"-to {end_timestamp}"
    cmd = f'static_ffmpeg -hide_banner -i "{infile}" -c:v libx264 {vf_scale_part} -preset veryslow -crf {crf} {from_stmt} {to_stmt} "{output_path}"'
    print_fcn(f"Executing:\n  {cmd}\n")
    rtn, _, _ = exec(cmd)
    if rtn != 0:
        print_fcn(f"{__file__}: WARNING: '{cmd}' returned code {rtn}")
    if not os.path.exists(output_path):
        print_fcn(f"Error, did not generate {output_path}")
        return False
    else:
        print_fcn(f"\nGenerated: {output_path}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Cuts clips from local files.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input", nargs="?")
    parser.add_argument("--start_timestamp", help="start of the clip")
    parser.add_argument("--end_timestamp", help="length of the clip")
    parser.add_argument("--outname", help="output name of the file")
    parser.add_argument(
        "--crf", default=_CRF_DEFAULT, type=int, help="crf quality of the file."
    )
    parser.add_argument("--height", help="height of the output video, e.g 1080 = 1080p")
    parser.add_argument(
        "--background",
        action="store_true",
        help="Use background thread to encode multiple videos",
    )
    args = parser.parse_args()

    is_interactive = (
        (args.start_timestamp is None)
        and (args.end_timestamp is None)
        and (args.outname is None)
        and (args.crf == _CRF_DEFAULT)
    )
    is_interactive = is_interactive or (args.background)

    infile = args.input or input("Input video: ")
    ext = os.path.splitext(infile)[1]
    count = 0
    executor = ThreadPoolExecutor(max_workers=1)
    futures = []

    while True:
        start_timestamp = args.start_timestamp or input("start_timestamp: ")
        end_timestamp = args.end_timestamp or input("end_timestamp: ")
        start_timestamp_str = sanitize(start_timestamp)
        end_timestamp_str = sanitize(end_timestamp)
        outpath_hint = (
            stripext(infile) + f"_clip_{start_timestamp_str}__{end_timestamp_str}{ext}"
        )
        output_path = args.outname or input(f"Output path [{outpath_hint}]: ")
        if output_path == "":
            output_path = outpath_hint
        else:
            # Auto-assume an mp4 extension if none is set.
            _, ext = os.path.splitext(output_path)
            if ext == "":
                output_path = output_path + ".mp4"
        # Silently handle collisions with an existing file.
        output_path = get_next_path(output_path)
        count += 1
        crf = args.crf  # The amount of quality, 0 is lossless and 50 is shit.

        print(infile)
        if not os.path.exists(infile):
            print(f"{infile} does not exist")
            sys.exit(1)

        def print_fcn(s):
            print(s)

        def task() -> bool:
            return encode(
                infile,
                args.height,
                crf,
                start_timestamp,
                end_timestamp,
                output_path,
                print_fcn=print_fcn,
            )

        if not is_interactive:
            task()
            break
        else:
            future = executor.submit(task)
            futures.append(future)
        if "y" not in input("Job is running\nSpecify another cut? (y/n): ").lower():
            break
        print("Waiting for jobs to finish...")
        args.start_timestamp = None
        args.end_timestamp = None
        args.outname = None
        args.output_path = None
    executor.shutdown(wait=True)


if __name__ == "__main__":
    main()
