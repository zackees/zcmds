import os

SELF_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(SELF_DIR, "..", ".."))
BIN_DIR = os.path.join(BASE_DIR, "bin")

assert os.path.exists(BIN_DIR), f"could not find {BIN_DIR}"


def main():
    cmds = os.listdir(BIN_DIR)
    cmds = [os.path.splitext(c)[0] for c in cmds if c.endswith(".bat") or c.endswith(".exe")]
    cmds.append("ytclip")
    cmds = list(set(cmds))
    cmds.sort()
    print("Commands:\n  " + "\n  ".join(cmds))
    return


if __name__ == "__main__":
    main()
