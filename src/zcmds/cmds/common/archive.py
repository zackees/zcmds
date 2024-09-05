import argparse
import os
import sys
import zipfile
from typing import Any, Optional


def zf_write(zf: zipfile.ZipFile, file_abs: str, archive_path: Optional[str]) -> None:
    print("compressing " + file_abs)
    try:
        zf.write(file_abs, archive_path)
    # permissions error
    except PermissionError:
        print("PermissionError: " + file_abs, file=sys.stderr)
    except FileNotFoundError:
        print("FileNotFoundError: " + file_abs, file=sys.stderr)
    except Exception as e:
        print("Exception: " + file_abs, file=sys.stderr)
        print(e, file=sys.stderr)


def get_paths(start_path: str) -> list[str]:
    out: list[str] = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            file_abs = os.path.join(root, file)
            out.append(file_abs)
    return out


def make_archive(
    folder_or_file: str,
    archive_name: str,
    root_dir: Optional[str] = None,
    no_deflate: bool = False,
) -> None:
    if archive_name is None:
        sanitized_name = folder_or_file
        # remove trailing slash
        if sanitized_name.endswith(os.sep):
            sanitized_name = sanitized_name[:-1]
        archive_name = sanitized_name + ".zip"
    root_dir = root_dir or os.path.dirname(folder_or_file)
    try:
        compression = zipfile.ZIP_STORED if no_deflate else zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(archive_name, "w", compression) as zf:
            if os.path.isfile(folder_or_file):
                zf_write(zf=zf, file_abs=folder_or_file, archive_path=None)
            else:
                paths: list[str] = get_paths(start_path=folder_or_file)
                for file_abs in paths:
                    print(f"compressing {file_abs}")
                    zf_write(
                        zf=zf,
                        file_abs=file_abs,
                        archive_path=os.path.relpath(file_abs, root_dir),
                    )

    except PermissionError as perm_err:
        print(perm_err, file=sys.stderr)


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
    parser.add_argument(
        "--no-deflate",
        action="store_true",
        help="Store files without compression",
    )
    return parser


def chop_ext(filename: str) -> str:
    is_file = os.path.isfile(filename)
    if not is_file:
        return filename
    return os.path.splitext(filename)[0]


def main_args(args: Any) -> int:
    folder_or_file = args.folder_or_file
    archive_name = args.archive_name or chop_ext(folder_or_file) + ".zip"
    make_archive(folder_or_file, archive_name, no_deflate=args.no_deflate)
    return 0


def main() -> int:
    args = make_argparse().parse_args()
    return main_args(args)


if __name__ == "__main__":
    main()
