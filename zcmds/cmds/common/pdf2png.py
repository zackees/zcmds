# pylint: skip-file


from pdf2image import convert_from_path  # type: ignore
import os
import sys


def main() -> None:
    infile = input("input pdf: ")
    page_start = int(input("first_page: "))
    page_last = int(input("last page: "))
    dpi = int(input("dpi: "))

    save_dir = os.path.splitext(infile)[0]
    os.makedirs(save_dir, exist_ok=True)
    infile = save_dir + ".pdf"
    images = convert_from_path(infile, first_page=page_start, last_page=page_last, dpi=dpi)
    for i, image in enumerate(images):
        output_png = os.path.join(save_dir, f"{i+page_start}.png")
        if os.path.isfile(output_png):
            os.remove(output_png)
        print(f"Writing: {output_png}")
        image.save(output_png)
        if not os.path.isfile(output_png):
            print(f"Error: could not save {output_png}")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except BaseException as e:
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
