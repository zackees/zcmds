# pylint: skip-file

"""
    Updater for zcmds.
"""

import sys
import os
import shutil

from zcmds.paths import BIN_DIR

SELF_DIR = os.path.dirname(__file__)

def remove_everything_in_dir(dir_path: str) -> None:
    if os.path.isdir(dir_path):
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

def main() -> None:
    # delete everything in BIN_DIR, if it exists.
    remove_everything_in_dir(BIN_DIR)
    if sys.platform == "darwin":
        from zcmds.install.darwin.update import main as darwin_update

        darwin_update()
    elif sys.platform == "win32":
        from zcmds.install.win32.update import main as win32_update

        win32_update()
    elif sys.platform == "linux":
        from zcmds.install.linux.update import main as linux_update

        linux_update()
    else:
        raise ValueError("Unhandled platform " + sys.platform)


if __name__ == "__main__":
    main()
