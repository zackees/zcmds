import sys
import os

SELF_DIR = os.path.dirname(__file__)


def main():
    if sys.platform == "darwin":
        from productivity_cmds.install.darwin import update
    elif sys.platform == "win32":
        from productivity_cmds.install.win32 import update
    else:
        raise ValueError("Unhandled platform " + sys.platform)
    update.main()


if __name__ == "__main__":
    main()
