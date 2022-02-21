# pylint: skip-file

"""
    Updater for zcmds.
"""

import sys
import os

SELF_DIR = os.path.dirname(__file__)


def main() -> None:
    if sys.platform == "darwin":
        from zcmds.install.darwin.update import main as linux_main
        linux_main()
    elif sys.platform == "win32":
        from zcmds.install.win32.update import main as win32_main
        win32_main()
    else:
        raise ValueError("Unhandled platform " + sys.platform)


if __name__ == "__main__":
    main()
