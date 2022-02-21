# pylint: skip-file

"""
    Updater for zcmds.
"""

import sys
import os

SELF_DIR = os.path.dirname(__file__)


def main():
    if sys.platform == "darwin":
        from zcmds.install.darwin import update
    elif sys.platform == "win32":
        from zcmds.install.win32 import update
    else:
        raise ValueError("Unhandled platform " + sys.platform)
    update.main()


if __name__ == "__main__":
    main()
