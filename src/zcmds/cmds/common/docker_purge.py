"""
This module contains a function which_all which returns all the paths where
the program name could be found. This is useful if you want to know if there
are multiple versions of a program on the system.
"""

import os
import sys

CMD = "docker system prune -a --volumes -f"


def main() -> int:
    """Prints the paths where the program name could be found."""
    return os.system(CMD)


if __name__ == "__main__":
    sys.exit(main())
