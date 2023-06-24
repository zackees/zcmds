"""
Convert an image to webp format.
"""


# pylint: skip-file

import argparse
import concurrent.futures
import os
import sys
import threading

from PIL import Image  # type: ignore

LOCK = threading.Lock()


def read_utf8(file: str) -> str:
    """Read a file as UTF-8."""
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


def write_utf8(file: str, content: str):
    """Write a file as UTF-8."""
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)


def convert_png_to_webp(file: str, scale: float, out_file: str) -> bool:
    im = Image.open(file)
    # Reduce the image size by half
    if scale != 1.0:
        new_size = (round(im.width * scale), round(im.height * scale))
        im.thumbnail(new_size, resample=Image.Resampling.LANCZOS, reducing_gap=3.0)
    try:
        # Save as webp
        im.save(fp=out_file, format="webp", optimize=True)
    except Exception as e:
        with LOCK:
            print(f"Failed to convert {file} to webp: {e}")
        return False
    # get size of original file
    original_size = os.path.getsize(file)
    # get size of webp file
    webp_size = os.path.getsize(out_file)  # change 'file' to 'out_file'
    # calculate savings
    savings = original_size - webp_size
    # print savings
    savings_perc = savings / original_size * 100
    with LOCK:
        print(
            f"Converting {file} to {out_file}, Saved {savings} bytes ({savings_perc:.2f}%)"
        )
    return True


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Converts image to webp\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="input", nargs="+")
    parser.add_argument(
        "--scale", help="Scale of the output image", default=1.0, type=float
    )
    parser.add_argument("--output_dir", help="Output directory", default=None)
    args = parser.parse_args()
    input_files = args.input
    outdir = args.output_dir
    if outdir is not None and not os.path.exists(outdir):
        os.makedirs(outdir)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process each file
        png_conversion_tasks = []
        for file in input_files:
            base_dir = outdir or os.path.dirname(file)
            filename, _ = os.path.splitext(os.path.basename(file))
            out_webp = os.path.join(base_dir, filename + ".webp")
            task = executor.submit(convert_png_to_webp, file, args.scale, out_webp)
            png_conversion_tasks.append(task)
        # Wait for all png conversions to complete
        success = True
        for task in concurrent.futures.as_completed(png_conversion_tasks):
            if not task.result():
                success = False
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
