# pylint: skip-file


import os
import sys
import traceback
from argparse import ArgumentParser

from pdf2image import convert_from_path  # type: ignore


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("input_pdf", help="input", nargs="?")
    parser.add_argument("--first_page", help="First page to include in the output.")
    parser.add_argument(
        "--last_page", help="Last page (inclusive) to include in the output."
    )
    parser.add_argument("--dpi", help="Dpi to render the output in")
    args = parser.parse_args()

    if args.input_pdf is None:
        args.input_pdf = input("input pdf: ")

    if args.first_page is None:
        args.first_page = int(input("first page: "))
        if args.first_page < 0:
            args.first_page = None

    if args.last_page is None:
        args.last_page = int(input("last page: "))
        if args.last_page < 0:
            args.last_page = None

    if args.dpi is None:
        args.dpi = int(input("dpi: "))

    save_dir = os.path.splitext(args.input_pdf)[0]
    os.makedirs(save_dir, exist_ok=True)
    infile = save_dir + ".pdf"
    images = convert_from_path(
        infile, first_page=args.first_page, last_page=args.last_page, dpi=args.dpi
    )
    for i, image in enumerate(images):
        output_png = os.path.join(save_dir, f"{i+args.first_page}.png")
        if os.path.isfile(output_png):
            os.remove(output_png)
        print(f"Writing: {output_png}")
        image.save(output_png)
        if not os.path.isfile(output_png):
            print(f"Error: could not save {output_png}")


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        traceback.print_exc()
        print(f"Error: could not convert pdf to png, because of {e}")
        if sys.platform == "win32":
            print("--> Try running `choco install poppler`")
        elif sys.platform == "darwin":
            print("--> Try running `brew install poppler`")
        elif sys.platform == "linux":
            print(
                "--> Try running `sudo apt-get install poppler-utils`"
            )  # Should this be poppler?
        else:
            print(f"Unexpected os {sys.platform}")
        sys.exit(1)
    sys.exit(0)
