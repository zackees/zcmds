"""
Convert an image to webp format.
"""

# pylint: skip-file

import argparse
import concurrent.futures
import os
import sys
import threading
import warnings
from dataclasses import dataclass
from typing import Optional

from PIL import Image  # type: ignore
from pillow_heif import register_heif_opener

register_heif_opener()


@dataclass
class ImageOptions:
    """Image options."""

    scale: float
    quality: Optional[int]
    subsampling: int
    height: Optional[int]


LOCK = threading.Lock()


def read_utf8(file: str) -> str:
    """Read a file as UTF-8."""
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


def write_utf8(file: str, content: str):
    """Write a file as UTF-8."""
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)


@dataclass
class ImageResult:
    success: bool
    original_size: int
    webp_size: int


def convert_img_to_format(
    file: str, out_file: str, options: ImageOptions
) -> ImageResult:
    """Convert a png file to webp."""
    assert out_file.lower().endswith(".webp") or out_file.lower().endswith(".jpg")
    assert file != out_file, "Input and output files must be different"
    assert os.path.exists(file), f"File {file} does not exist"
    format = out_file.split(".")[-1]
    assert format in ["webp", "jpg"]
    if format == "jpg":
        format = "jpeg"
    im = Image.open(file)
    # Convert the image to RGB if it's RGBA and the output format is JPEG
    if im.mode == "RGBA" and format == "jpeg":
        im = im.convert("RGB")  # type: ignore
    # Reduce the image size by half
    if options.height is not None:
        height = options.height
        new_size = (round(height * im.width / im.height), height)
        im.thumbnail(new_size, resample=Image.Resampling.LANCZOS, reducing_gap=3.0)
    elif options.scale != 1.0:
        new_size = (round(im.width * options.scale), round(im.height * options.scale))
        im.thumbnail(new_size, resample=Image.Resampling.LANCZOS, reducing_gap=3.0)
    try:
        quality = options.quality if options.quality is not None else 80
        # Save as webp
        im.save(
            fp=out_file,
            format=format,
            optimize=True,
            quality=quality,
            method=6,
            subsampling=options.subsampling,
        )
    except Exception as e:
        with LOCK:
            print(f"Failed to convert {file} to {format}: {e}")
        return ImageResult(success=False, original_size=0, webp_size=0)
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
    return ImageResult(success=True, original_size=original_size, webp_size=webp_size)


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
    parser.add_argument(
        "--quality", help="Quality of the output image", default=None, type=int
    )
    parser.add_argument(
        "--height", type=int, help="Height of the output image", default=None
    )
    parser.add_argument(
        "--subsampling",
        help="Subsampling of the output image, 0 represents 4:4:4, 1 represents 4:2:2, 2 represents 4:2:0",
        default=0,
        type=int,
        choices=[0, 1, 2],
    )
    parser.add_argument(
        "--format",
        help="Format of the output image",
        default="webp",
        choices=["webp", "jpg"],
    )
    parser.add_argument("--output_dir", help="Output directory", default=None)
    args = parser.parse_args()
    input_files = args.input
    outdir = args.output_dir
    subsampling = args.subsampling
    format = args.format
    if subsampling != 0 and args.format == "webp":
        warnings.warn("Subsampling is not supported in webp as of June 2023")
    image_options = ImageOptions(
        scale=args.scale,
        quality=args.quality,
        subsampling=subsampling,
        height=args.height,
    )
    if outdir is not None and not os.path.exists(outdir):
        os.makedirs(outdir)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process each file
        png_conversion_tasks = []
        for file in input_files:
            base_dir = outdir or os.path.dirname(file)
            filename, _ = os.path.splitext(os.path.basename(file))
            out_webp = os.path.join(base_dir, filename + f".{format}")
            if os.path.abspath(file) == os.path.abspath(out_webp):
                out_webp = os.path.join(base_dir, filename + f".1.{format}")
            task = executor.submit(
                convert_img_to_format,
                file=file,
                out_file=out_webp,
                options=image_options,
            )
            png_conversion_tasks.append(task)
        # Wait for all png conversions to complete
        success = True
        for task in png_conversion_tasks:
            result = task.result()
            if not result.success:
                success = False
            else:
                original_size, webp_size = result.original_size, result.webp_size
                shrinkage_percentage = 100 * (original_size - webp_size) / original_size
                print(f"Shrinkage: {shrinkage_percentage:.2f}%")
                print(f"    Input image size: {original_size:,} bytes")
                print(f"    Output image size: {webp_size:,} bytes")
    return 0 if success else 1


if __name__ == "__main__":
    infile = (
        r"C:\Users\niteris\dev\zcmds\321862084-f6c169e1-69db-47ef-94a3-3b72f66a14b0.png"
    )
    scale = 2
    sys.argv.append(infile)
    sys.argv.append("--scale")
    sys.argv.append(str(scale))
    sys.exit(main())
