import argparse
import os
import sys
import zipfile
from typing import Optional


def make_archive(
    folder_or_file: str, archive_name: str, root_dir: Optional[str] = None
) -> None:
    if archive_name is None:
        archive_name = folder_or_file + ".zip"
    root_dir = root_dir or os.path.dirname(folder_or_file)
    with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zf:
        if os.path.isfile(folder_or_file):
            zf.write(folder_or_file)
        else:
            for root, dirs, files in os.walk(folder_or_file):
                for file in files:
                    print("compressing " + file)
                    file_abs = os.path.join(root, file)
                    zf.write(file_abs, os.path.relpath(file_abs, root_dir))


def make_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Make archive of folder or file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "folder_or_file",
        help="Folder or file to archive",
    )
    parser.add_argument(
        "archive_name",
        help="Name of archive",
        nargs="?",
    )
    return parser


def chop_ext(filename: str) -> str:
    is_file = os.path.isfile(filename)
    if not is_file:
        return filename
    return os.path.splitext(filename)[0]


def main() -> int:
    args = make_argparse().parse_args()
    folder_or_file = args.folder_or_file
    archive_name = args.archive_name or chop_ext(folder_or_file) + ".zip"
    make_archive(folder_or_file, archive_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
