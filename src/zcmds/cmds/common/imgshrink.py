"""
Convert an image to webp format.
"""


import argparse
import os
import sys


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Converts image to webp\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input")
    parser.add_argument(
        "--scale", help="Scale of the output image", default=0.5, type=float
    )
    parser.add_argument(
        "--height", type=int, help="Height of the output image", default=None
    )
    parser.add_argument(
        "--quality", help="Quality of the output image", default=80, type=int
    )
    args = parser.parse_args()
    infile = args.input
    scale = args.scale
    quality = args.quality

    scale_stmt = ""
    height_stmt = ""

    if args.height is not None:
        height_stmt = f"--height {args.height}"
    else:
        scale_stmt = f"--scale {scale}"

    cmd = f'img2webp "{infile}" {scale_stmt} {height_stmt} --quality {quality} --format webp --quality {quality}'
    rtn = os.system(cmd)
    if rtn != 0:
        print(f"Failed to convert {infile}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
