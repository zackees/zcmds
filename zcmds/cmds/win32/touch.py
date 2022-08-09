import argparse
from pathlib import Path


def main() -> int:
    """Touches a file."""
    argparser = argparse.ArgumentParser(description="Simply touches a file.")
    argparser.add_argument("file", help="The file to touch.")
    args = argparser.parse_args()
    Path(args.file).touch()
    return 0
