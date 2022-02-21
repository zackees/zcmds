import os
import sys

from zcmds.cmds.common import update

SELF_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(SELF_DIR, "..", ".."))
BIN_DIR = os.path.join(BASE_DIR, "bin")

os.makedirs(BIN_DIR, exist_ok=True)


def main():
    if "update" in sys.argv:
        update.main()
        return
    cmds = os.listdir(BIN_DIR)
    cmds = [
        os.path.splitext(c)[0] for c in cmds if c.endswith(".bat") or c.endswith(".exe")
    ]
    cmds.append("ytclip")
    cmds = list(set(cmds))
    if "update" in cmds:
        cmds.remove("update")
    cmds.append("zcmds update")
    cmds.append("zcmds_install")
    cmds.sort()
    print("Commands:\n  " + "\n  ".join(cmds))
    return


if __name__ == "__main__":
    main()
