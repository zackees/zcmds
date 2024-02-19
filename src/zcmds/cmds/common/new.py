"""
Opens a new shell in a new terminal window.
"""

import os
import sys


def main() -> int:
    if sys.platform == "win32":
        os.system("start cmd")
    elif sys.platform == "darwin":
        os.system("open -a Terminal")
    elif sys.platform == "linux":
        os.system("gnome-terminal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
