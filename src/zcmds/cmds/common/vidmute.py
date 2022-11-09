# pylint: skip-file

import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def _make_output_name(in_file: str) -> str:
    pathname, extension = os.path.splitext(in_file)
    out_file = f"{pathname}_mute{extension}"
    return out_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Removes an audio track from a source\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="Filename to strip audio out of")
    parser.add_argument(
        "output",
        nargs="?",
        help="Optional output file, other wise a new file is created with <filename>_strip_audio.<ext>",
    )
    args = parser.parse_args()
    input_file = args.input or input("")
    output = args.output or _make_output_name(input_file)

    error_code = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        # temporary directory allows use the use case of input and output
        # name being the same.
        tempout = os.path.join(tmpdir, "file.mp4")
        cmd = f'static_ffmpeg -hide_banner -v quiet -stats -i "{input_file}" -c copy -an "{tempout}"'
        try:
            subprocess.check_output(cmd, shell=True)
            shutil.copyfile(tempout, output)
        except subprocess.CalledProcessError as cpe:
            print(
                f"{__file__}: Error while processing {cmd} because of {cpe}"
                f"\nSTDOUT\n#################\n{cpe.output}"
            )
            error_code = cpe.returncode
    print(f"\n\nCompleted! Output file: {output}")
    sys.exit(error_code)


if __name__ == "__main__":
    main()
