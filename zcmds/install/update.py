# pylint: skip-file

"""
    Updater for zcmds.
"""

import os
import shutil
import sys

from zcmds.paths import BIN_DIR

SELF_DIR = os.path.dirname(__file__)


def remove_everything_in_dir(dir_path: str) -> None:
    if os.path.isdir(dir_path):
        for file_name in os.listdir(dir_path):
            try:
                file_path = os.path.join(dir_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)
            except OSError as err:
                print("Error removing file: " + str(err))


def main() -> None:
    # delete everything in BIN_DIR, if it exists.
    remove_everything_in_dir(BIN_DIR)
    if sys.platform == "darwin":
        from zcmds.install.darwin import darwin_update  # pytype: disable=import-error

        darwin_update.main()
    elif sys.platform == "win32":
        from zcmds.install.win32 import win32_update  # pytype: disable=import-error

        win32_update.main()
    elif sys.platform == "linux":
        from zcmds.install.linux import linux_update  # pytype: disable=import-error

        linux_update.main()
    else:
        raise ValueError("Unhandled platform " + sys.platform)


if __name__ == "__main__":
    main()
