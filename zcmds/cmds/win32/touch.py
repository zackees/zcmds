import sys
from pathlib import Path


def main() -> int:
    """Touches a file."""
    file = sys.argv[1]
    Path(file).touch()
    return 0
